$(document)
  .ready(function() {
    xhr = null;
    timeout = 0;
    refreshCookie();
    addIcons();
    updateLastPlayed();
    updateCharts();
  })

function updateLastPlayed() {
  setInterval(function() {
    loadResults(["/last_played/", $("#last-played")]);
  }, 60000);
}

function updateCharts() {
  setInterval(function() {
    loadResults(["/charts/", $("#charts")]);
  }, 86400000);
}

function addIcons() {
  $(".search-button").html("<i class='fa fa-search icon'></i>");
  var login_buttons = $("#login-buttons");
  if (login_buttons.length) {
    login_buttons.find("#login-tab")[0].href = "#tabs-login";
    login_buttons.find("#signup-tab")[0].href = "#tabs-signup";
    $("#google-icon").html("<i class='fab fa-google icon'></i>");
  }
  var view_buttons = $(".view-button");
  if (view_buttons.length) {
    view_buttons.each(function() {
      if ($(this).innerText == 'List') {
        $(this).html("<i class='fas fa-th d-none'></i><i class='fas fa-bars'></i>");
      } else {
        $(this).html("<i class='fas fa-th'></i><i class='fas fa-bars d-none'></i>");
      }
    })
  }
  var view_buttons = $(".episode-buttons");
  if (view_buttons.length) {
    view_buttons.each(function() {
      $(this).find(".playlist-remove").html("<i class='fas fa-times-circle'></i>");
      $(this).find(".playlist-move-up").html("<i class='fas fa-arrow-circle-up'></i>");
      $(this).find(".playlist-move-down").html("<i class='fas fa-arrow-circle-down'></i>");
    })
  }
  var back_buttons = $(".results-back");
  if (back_buttons.length) {
    back_buttons.each(function() {
      $(this).html("<i class='fas fa-arrow-circle-left'></i>");
    })
  }
  var minimize_buttons = $(".results-minimize");
  if (minimize_buttons.length) {
    minimize_buttons.each(function() {
      $(this).html("<i class='fas fa-minus-circle icon'></i>");
    })
  }
  var close_buttons = $(".results-close");
  if (close_buttons.length) {
    close_buttons.each(function() {
      $(this).html("<i class='fas fa-times-circle icon'></i>");
    })
  }
}

// HISTORY API
$(window).on("popstate", function(event) {
  var state = event.originalEvent.state;
  if (state) {
    var el = $("#main")[0];
    $(el).html(state.context);
    $("title")[0].innerText = state.title;
  }
})
function pushState(url) {
  var urls = ["dopebar", "charts", "episodes", "last_played", "unsubscribe"];
  for (i = 0; i < urls.length; i++) {
    if (url.includes(urls[i])) {
      return;
    }
  }
  var el = $("#main")[0];
  var context = el.innerHTML;
  var title = updateTitle();
  var state = {
    "context": context,
    "title": title,
  };
  history.pushState(state, "", url);
}
function replaceState(url) {
  if (!url || url.includes("unsubscribe") || url.includes("episodes")) {
    url = $("#main")[0].baseURI;
  }
  var urls = ["dopebar", "charts", "last_played"];
  for (i = 0; i < urls.length; i++) {
    if (url.includes(urls[i])) {
      return;
    }
  }
  var el = $("#main")[0];
  var context = el.innerHTML;
  var title = updateTitle();
  var state = {
    "context": context,
    "title": title,
  };
  history.replaceState(state, "", url);
}
function updateTitle() {
  // TODO center-stage contains title string
  var title = "dopepod";
  var el = $("#player-wrapper");
  if (el.length) {
    title = el.find("#player-title")[0].innerText;
    var episode = el.find("#player-episode")[0].innerText;
    title = "Now playing: " + title + " - " + episode + " | dopepod";
  }
  else if ($("#showpod-c").length) {
      title = "Listen to episodes of " + $("#showpod-title")[0].innerText + " on dopepod";
  }
  $("title")[0].innerText = title;
  return title;
}

// PAGE REFRESH STUFF
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function refreshCookie() {
  // for sending csrf token on every ajax POST request
  var csrftoken = getCookie("csrftoken");
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });
}
function refreshPage() {
  var url = "/dopebar/";
  var drop = $("#dopebar");
  loadResults([url, drop, loadResults, ["/", "#center-stage", loadResults, ["/last_played/", "#last-played"]]]);
}
function checkForXHR(url) {
  var urls = ["dopebar", "charts", "episodes", "last_played"];
  for (i = 0; i < urls.length; i++) {
    if (url.includes(urls[i])) {
      return;
    }
  }
  if(xhr != null) {
    xhr.abort();
    xhr = null;
  }
}

// LOADER
function loadResults(args) {
  var url = args[0];
  var drop = $(args[1]);
  var callback = args[2];
  var args = args[3];
  checkForXHR(url);
  pushState(url);
  if (!drop.find(".circle-loading").length && url != "/dopebar/" && url != "/last_played/") {
    var loading = $(".circle-loading").clone();
    drop.html(loading);
  }
  xhr = $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
  })
    .done(function(response) {
       drop.html(response);
      if (callback) {
        callback(args);
      }
      else {
        $(".episodes-button").text("Episodes");
        clearTimeout(timeout);
        timeout = setTimeout(function() {
          $("#dopebar-collapse.show").collapse("hide");
        }, 1000)
      }
      replaceState(url);
    });
}

// SCROLLERS
function scrollToTop() {
  $("html, body").animate({
    scrollTop: $("body").offset().top
  }, 250);
}
function scrollToCharts() {
  $("html, body").animate({
    scrollTop: $("#left").offset().top - 44
  }, 250);
}
function scrollToLastPlayed() {
  $("html, body").animate({
    scrollTop: $("#right").offset().top - 44
  }, 250);
}
function scrollText(box, text) {
  var boxWidth = box.innerWidth();
  var textWidth = text.width();
  if (textWidth > boxWidth + 5) {
    var animSpeed = textWidth * 30;
    $(box)
      .animate({scrollLeft: (textWidth - boxWidth)}, animSpeed)
      .animate({scrollLeft: 0}, animSpeed, function() {
        setTimeout(function() {
          scrollText(box, text);
        }, 1000);
      })
  }
}
function changeTheme(theme) {
  if (theme) {
    $("body").addClass("darken");
  }
  else {
    $("body").removeClass("darken");
  }
}
function subscribeOrUnsubscribe(form) {
  var url = form.action;
  var method = form.method;
  form = $(form);
  form.find(".sub-button").html(getButtonLoading());
  var podid = form.find("input[name=podid]").val();
  var data = {
    "podid": podid,
  };
  $.ajax({
    method: method,
    url: url,
    data: data,
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
      $("#center-stage").html(xhr.responseText);
      replaceState("/");
    })
    .done(function(response) {
      $("#center-stage").html(response);
      var url = "/episodes/" + podid + "/";
      var drop = $("#episodes-collapse");
      loadResults([url, drop]);
    });
};

function replaceChars(q) {
  q = q.replace(/&+/g, "+");
  q = q.replace(/\s+/g, "+");
  q = q.replace(/([^a-zA-Z0-9\u0080-\uFFFF +']+)/gi, "");
  return q;
}

function cookieBannerClose() {
  $("#player").empty();
}

function getButtonLoading() {
  return $(".button-loading").first().clone();
}

$(document)
  // SEARCH
  // search when user types into search field (with min "delay" between keypresses)
  .on("keyup submit", ".search-form", function(e) {
    e.preventDefault();
    var url = this.action;
    var form = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var q = form.find(".q").val();
      if (q) {
        q = replaceChars(q);
        var drop = $("#center-stage");
        url = url + '?q=' + q;
        if (!(drop.find(".results-header").data("q") == q)) {
          loadResults([url, drop]);
        }
        scrollToTop();
      }
    }, 250);
  })
  // search when user clicks buttons
  .on("click", "a.alphabet-button, a.options-button, a.provider-button", function(e) {
    e.preventDefault();
    var url = this.href;
    var button = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = $(button.parents(".results").parent());
      loadResults([url, drop]);
    }, 250);
  })
  // NAVIGATION
  .on("click", ".showpod", function(e) {
    e.preventDefault();
    var url = this.href;
    var button = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var podid = button.data("podid");
      var drop = $("#center-stage");
      if (!(drop.find("#showpod-c").data("podid") == podid)) {
        var args = ["/episodes/" + podid + "/", "#episodes-collapse"];
        loadResults([url, drop, loadResults, args]);
      }
      scrollToTop();
    }, 250);
  })
  .on("click", ".index-link", function(e) {
    e.preventDefault();
    var url = this.href;
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = $("#center-stage");
      if (!drop.find("#login-wrapper").length && !drop.find("#dashboard").length) {
        loadResults([url, drop]);
      }
      else {
        $("#splash-tab").tab("show");
      }
      scrollToTop();
    }, 250);
  })
  .on("click", ".browse-link", function(e) {
    e.preventDefault();
    var url = this.href;
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = $("#center-stage");
      if (!drop.find(".list").length) {
        loadResults([url, drop]);
      }
      scrollToTop();
    }, 250);
  })
  .on("click", ".charts-link", function(e) {
    e.preventDefault();
    scrollToCharts();
  })
  .on("click", ".last-played-link", function(e) {
    e.preventDefault();
    scrollToLastPlayed();
  })
  .on("click", ".subscriptions-link", function(e) {
    e.preventDefault();
    var url = this.href;
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = $("#center-stage");
      if (!drop.find(".subscriptions").length) {
        loadResults([url, drop]);
      }
      scrollToTop();
    }, 250);
  })
  .on("click", ".settings-link", function(e) {
    e.preventDefault();
    var url = this.href;
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = $("#center-stage");
      if (!drop.find("#settings").length) {
        loadResults([url, drop]);
      }
      scrollToTop();
    }, 250);
  })
  .on("click", ".playlist-link", function(e) {
    e.preventDefault();
    var url = this.href;
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = $("#center-stage");
      if (!drop.find(".playlist").length) {
        loadResults([url, drop]);
      }
      scrollToTop();
    }, 250);
  })
  // FORMS
  .on("submit", ".settings-form", function (e) {
    e.preventDefault();
    var method = this.method;
    var url = this.action;
    var data = $(this).serialize();
    var button = $(this).find(".settings-save");
    var text = button[0].innerText;
    button.html(getButtonLoading());
    var theme = $(this).find("input[name=dark_theme]").is(":checked");
    $.ajax({
      data: data,
      method: method,
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        button.text(text);
        $("#center-stage").html(xhr.responseText);
        scrollToTop();
      })
      .done(function(response) {
        changeTheme(theme);
        $("#center-stage").html(response);
        scrollToTop();
      });
  })
  .on("submit", "#sub-form", function(e) {
    e.preventDefault();
    subscribeOrUnsubscribe(this);
  })
  .on("submit", ".playlist-form", function(e) {
    e.preventDefault();
    var data = $(this).serialize();
    var url = this.action;
    var method = this.method;
    var mode = $(this).find("input[name=mode]").val();
    var button = $(this).find("button");
    var text = button[0].innerText;
    button.html(getButtonLoading());
    $.ajax({
      method: method,
      url: url,
      data: data,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        button.text(text);
      })
      .done(function(response) {
        if (mode == "play") {
          var player = $("#player");
          player.removeClass("minimize");
          player.html(response);
          updateTitle();
          button.text(text);
          // gotta wait a sec here
          setTimeout(function() {
            var box = $("#player-title");
            var text = $("#player-title h1");
            scrollText(box, text);
          }, 1000);
        }
        else if (mode == "add") {
          button.text(text);
        }
        else {
          var drop = $("#center-stage");
          loadResults(["/playlist/", drop]);
        }
      });
  })
  // close player
  .on("click", "#player-close", function(e) {
    e.preventDefault();
    $("#audio-el audio")[0].preload="none";
    $("#player").empty();
    $("#player").removeClass("minimize");
    updateTitle();
  })
  .on("click", "#player-minimize", function(e) {
    e.preventDefault();
    if ($("#player").hasClass("minimize")) {
      $("#player").removeClass("minimize");
      $("#audio-el").removeClass("d-none");
      $(this).removeClass("active");
    }
    else {
      $("#player").addClass("minimize");
      $("#audio-el").addClass("d-none");
      $(this).addClass("active");
    }
  })
  // LOGIN & SIGNUP
  // open login / register
  .on("click", ".ajax-login, .ajax-signup", function(e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    if (!drop.find("#login-wrapper").length && !drop.find("#dashboard").length) {
      loadResults([url, drop]);
    }
    else if ($(this).hasClass("ajax-login")) {
      $("#login-tab").tab("show");
    }
    else {
      $("#signup-tab").tab("show");
    }
    scrollToTop();
  })
  .on("click", ".password-link", function(e) {
    e.preventDefault();
    $("#password-tab").tab("show");
  })
  .on("click", ".login-toggle", function() {
    $(".error-message").remove();
  })
  // login or signup, refresh after
  .on("submit", ".login-form, .signup-form", function (e) {
    e.preventDefault();
    var data = $(this).serialize();
    var method = this.method;
    var url = this.action;
    var button = $(this).find(".login-button");
    var text = button[0].innerText;
    button.html(getButtonLoading());
    $.ajax({
      data: data,
      method: method,
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        button.text(text);
        $("#center-stage").html(xhr.responseText);
        scrollToTop();
      })
      .done(function(response) {
        refreshCookie();
        refreshPage();
        scrollToTop();
        });
  })
  .on("submit", ".password-form", function (e) {
    e.preventDefault();
    var data = $(this).serialize();
    var method = this.method;
    var url = this.action;
    var button = $(this).find(".password-button");
    var text = button[0].innerText;
    button.html(getButtonLoading());
    $.ajax({
      data: data,
      method: method,
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        button.text(text);
        $("#center-stage").html(xhr.responseText);
        scrollToTop();
      })
      .done(function(response) {
        $("#center-stage").html(response);
        scrollToTop();
      });
  })
  .on("click", ".results-close", function(e) {
    e.preventDefault();
    $(this).parents(".results").remove();
    var drop = $("#center-stage");
    loadResults(["/", drop]);
    scrollToTop();
  })
  .on("click", ".view-button", function(e) {
    e.preventDefault();
    var collapses = $(this).parents(".results").find($(".results-collapse"));
    collapses.each(function() {
      $(this).collapse("toggle");
    })
    $(this).children().each(function() {
      $(this).toggleClass("d-none");
    });
  })
  .on("mouseenter mouseleave", ".view-button, .provider-button", function() {
    $(this).children().each(function() {
      $(this).toggleClass("d-none");
    });
  })
  // BOOTSTRAP COLLAPSES
  .on("show.bs.collapse", ".more-collapse", function(e) {
    e.stopPropagation()
    $(".more-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".last-played-collapse", function(e) {
    $(".last-played-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".options-collapse", function (e) {
    $(".options-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".showpod-collapse", function (e) {
    $(".showpod-collapse.show").collapse("hide");
  })
  .on("click", ".lights-toggle", function(e) {
    e.preventDefault();
    var el = $("body");
    if (el.hasClass("darken")) {
      el.removeClass("darken");
    }
    else {
      el.addClass("darken");
    }
  })
  .on("click", ".btn-dope, .dopebar-link, .last-played-toggle, #episodes-table tbody tr", function(e) {
    $(this).blur();
  })
  .on("click", "body, .dopebar-link", function(e) {
    $("#dopebar-collapse.show").collapse("hide");
  })
  .on("click", "#dopebar", function(e) {
    e.stopPropagation();
  })
  .on("click", ".select-subscription", function() {
    var button = $(this);
    if (button.hasClass("active")) {
      button.removeClass("active");
      button.parent().removeClass("active");
    }
    else {
      button.addClass("active");
      button.parent().addClass("active");
    }
  })
  .on("click", ".unsubscribe-button", function(e) {
    e.preventDefault();
    var url = this.href;
    var buttons = $(this).parents(".results").find($(".select-subscription.active"));
    var podids = [];
    buttons.each(function(i, button) {
      podids[i] = $(button).data("podid");
    })
    var data = {
      "podids": podids,
    }
    var button = $(this);
    var text = button[0].innerText;
    button.html(getButtonLoading());
    $.ajax({
      method: "POST",
      url: url,
      data: data,
    })
    .fail(function(xhr, ajaxOptions, thrownError) {
      button.text(text);
      $("#center-stage").html(xhr.responseText);
      replaceState("/");
    })
    .done(function(response) {
      $("#center-stage").html(response);
      replaceState(url);
    });
  })
