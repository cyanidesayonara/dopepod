// after page loads
$(document)
  .ready(function() {
    xhr = null;
    timeout = 0;
    refreshCookie();
    collapseCollapses();
    addIcons();
    showpodBadge();
    scrollSpy();
  })

function addIcons() {
  $("#search-button").html("<i class='fa fa-search icon'></i>");
  var login_buttons = $("#login-buttons");
  if (login_buttons.length) {
    login_buttons.find("#login-tab")[0].href = "#tabs-login";
    login_buttons.find("#signup-tab")[0].href = "#tabs-signup";
    $("#google-icon").html("<i class='fab fa-google icon'></i>");
  }
  var view_buttons = $(".results-buttons");
  if (view_buttons.length) {
    view_buttons.each(function() {
      $(this).find(".view-icon-grid").html("<i class='fas fa-th'></i>");
      $(this).find(".view-icon-list").html("<i class='fas fa-bars'></i>");
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

function collapseCollapses() {
  var el = $("#episodes-table");
  if (el.length) {
    var collapses = el.find(".more-collapse");
    collapses.each(function() {
      $(this).collapse("hide");
    })
  }
}

function scrollSpy() {
  $(window).scroll(function () {
    showpodBadge();
  })
}

function showpodBadge() {
  var scroll = $(window).scrollTop();
  if (scroll > 300) {
    $(".showpod-image").addClass("showpod-badge");
  }
  else {
    $(".showpod-image").removeClass("showpod-badge");
  }
}

// HISTORY API
$(window).on("popstate", function(event) {
  var state = event.originalEvent.state;
  if (state) {
    $("#main-wrapper").html(state.context);
    $("title")[0].innerText = state.title;
  }
})
function pushState() {
  var el = $("#main-wrapper")[0];
  var context = el.innerHTML;
  var url = el.baseURI;
  var title = "dopepod";
  var state = {
    "context": context,
    "title": title,
  };
  history.pushState(state, "", url);
  updateTitle();
}
function replaceState(url) {
  var el = $("#main-wrapper")[0];
  var context = el.innerHTML;
  var title = "dopepod";
  var state = {
    "context": context,
    "title": title,
  };
  if (url.includes("charts")) {
    var url = "/";
  }
  history.replaceState(state, "", url);
  updateTitle();
}
function updateTitle() {
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
  checkForXHR();
  $.ajax({
    type: "GET",
    url: "/dopebar/",
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
    })
    .done(function(response) {
      $("#episodes").empty();
      $("#results").empty();
      var drop = $("#charts");
      loadResults("/charts/", drop);
      $("#dopebar-drop").html(response);
    });
}

function checkForXHR() {
  if(xhr != null) {
    xhr.abort();
    xhr = null;
  }
}

// LOADERS
function loadEpisodes(podid) {
  $("#episodes-collapse").load("/static/loading.html");
  $.ajax({
    method: "POST",
    url: "/episodes/",
    data: {
      "podid": podid,
    },
  })
    .fail(function(xhr, ajaxOptions, thrownError){
    })
    .done(function(response) {
      if ($("#showpod-c").length) {
        $("#episodes-collapse").html(response);
        var url = $("#main-wrapper")[0].baseURI;
        replaceState(url);
      }
    });
}
function loadResults(url, drop, podid) {
  checkForXHR();
  $(drop).load("/static/loading.html");
  xhr = $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
  })
    .done(function(response) {
      drop.html(response);
      if (podid) {
        loadEpisodes(podid);
      }
      replaceState(url);
    });
}

// SCROLLTO
function scrollToTop() {
  $("html, body").animate({
    scrollTop: $("body").offset().top
  }, 250);
}
function scrollToMultibar() {
  $("html, body").animate({
    scrollTop: 400
  }, 250);
}
function scrollText(box, text) {
  var boxWidth = box.innerWidth();
  var textWidth = text.width();
  if (textWidth > boxWidth) {
    var animSpeed = textWidth * 20;
    $(box)
      .animate({scrollLeft: (textWidth - boxWidth)}, animSpeed)
      .animate({scrollLeft: 0}, animSpeed, function() {
        scrollText(box, text);
      })
  }
}

$(document)
  .on("webkitAnimationEnd oanimationend msAnimationEnd animationend", "#nothing", function(e) {
    $(".logo-wrapper").children().each(function() {
      $(this).addClass("logo-final");
    })
  })
  // SEARCH
  // search when user types into search field (with min "delay" between keypresses)
  .on("keyup", "#search-form", function() {
    var el = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var q = $("#q").val();
      if (q && /^[\w\d ]+$/.test(q)) {
        var url = el[0].action;
        var drop = $("#search");
        url = url + '?q=' + q;
        pushState();
        loadResults(url, drop);
      }
    }, 250);
  })
  // search when "search" button is clicked
  .on("submit", "#search-form", function(e) {
    e.preventDefault();
    var el = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = el[0].action;
      var drop = $("#search");
      var q = $("#q").val();
      if (q && /^[\w\d ]+$/.test(q)) {
        url = url + '?q=' + q;
        pushState();
        loadResults(url, drop);
      }
    }, 250);
  })
  // search when user clicks buttons
  .on("click", ".page-buttons a, .genre-buttons a, .language-buttons a, .alphabet-buttons a, .genre_rank a", function(e) {
    e.preventDefault();
    var el = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = el[0].href;
      var drop = $(el.parents(".results").parent()[0]);
      pushState();
      loadResults(url, drop);
      $("#q").val("");
    }, 250);
  })
  // NAVIGATION
  .on("click", ".showpod", function(e) {
    e.preventDefault();
    var el = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = el[0].href;
      var podid = el.data("podid");
      var drop = $("#center-stage");
      if (!(drop.find("#showpod-c").data("podid") == podid)) {
        pushState();
        loadResults(url, drop, podid);
        $("#q").val("");
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
      if (!drop.find("#dashboard-top").length) {
        pushState();
        loadResults(url, drop);
        $("#q").val("");
      }
      $("#search").empty();
      scrollToTop();
    }, 250);
  })
  .on("click", ".browse-link", function(e) {
    e.preventDefault();
    var url = this.href;
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = $("#search");
      pushState();
      loadResults(url, drop);
      $("#q").val("");
      scrollToTop();
    }, 250);
  })
  .on("click", ".charts-link", function(e) {
    e.preventDefault();
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = $("#search");
      $("#q").val("");
      $("#search").empty();
      scrollToTop();
    }, 250);
  })
  .on("click", ".subscriptions-link", function(e) {
    e.preventDefault();
    var url = this.href;
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = $("#search");
      pushState();
      loadResults(url, drop);
      $("#q").val("");
      scrollToTop();
    }, 250);
  })
  // open settings
  .on("click", ".settings-link", function(e) {
    e.preventDefault();
    var url = this.href;
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = $("#center-stage");
      if (!drop.find("#settings").length) {
        pushState();
        $("#q").val("");
        loadResults(url, drop);
      }
      scrollToTop();
    }, 250);
  })
  // FORMS
  .on("submit", "#settings-form", function (e) {
    e.preventDefault();
    var button = $(this).find("#settings-save");
    button.text("Saving...");
    var data = $(this).serialize();
    var theme = $("input[name=dark_theme]").is(":checked");
    var method = this.method;
    var url = this.action;
    $.ajax({
      data: data,
      method: method,
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        pushState();
        $("#center-stage").html(xhr.responseText);
        button.text("Save");
      })
      .done(function(response) {
        button.text("Saved");
        var drop = $("#center-stage");
        pushState();
        loadResults("/", drop);
        scrollToTop();
        if (theme) {
          $("body").addClass("darken");
        }
        else {
          $("body").removeClass("darken");
        }
      });
  })
  .on("submit", "#sub-form", function(e) {
    e.preventDefault();
    var form = $(this);
    var button = form.find(".sub-button");
    button.text("Loading...");
    var data = form.serialize();
    var url = this.action;
    var method = this.method;
    $.ajax({
      method: method,
      url: url,
      data: data,
    })
      .fail(function(xhr, ajaxOptions, thrownError){
        var drop = $("#center-stage");
        loadResults("/", drop);
      })
      .done(function(response) {
        var podid = form.find("input[name=podid]").val();
        var url = $("#main-wrapper")[0].baseURI;
        var drop = $("#center-stage");
        loadResults(url, drop, podid);
        replaceState(url);
      });
  })
  // PLAYER
  // put episode in player
  .on("click", ".play", function(e) {
    e.preventDefault();
    var data = $(this).serialize();
    var url = this.action;
    var method = this.method;
    $.ajax({
      method: "POST",
      url: "/play/",
      data: data,
    })
      .fail(function(xhr, ajaxOptions, thrownError){
      })
      .done(function(response) {
        var player = $("#player-drop");
        $("#player-drop").removeClass("minimize");
        player.html(response);
        updateTitle();
        var box = $("#player-title");
        var text = $("#player-title span");
        scrollText(box, text);
      });
  })
  // close player
  .on("click", "#player-close", function(e) {
    e.preventDefault();
    $("#audio-el").preload="none";
    $("#player-drop").empty();
    $("#player-drop").removeClass("minimize");
    updateTitle();
  })
  .on("click", "#player-minimize", function(e) {
    e.preventDefault();
    if ($("#player-drop").hasClass("minimize")) {
      $("#player-drop").removeClass("minimize");
      $("#player-bottom").removeClass("d-none");
      $(this).removeClass("active");
    }
    else {
      $("#player-drop").addClass("minimize");
      $("#player-bottom").addClass("d-none");
      $(this).addClass("active");
    }
  })
  // LOGIN & SIGNUP
  // open login / register
  .on("click", ".ajax-login, .ajax-signup", function(e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    pushState();
    loadResults(url, drop);
    $("#q").val("");
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
    var button = $(this).find(".login-button");
    button.text("Loading...");
    var data = $(this).serialize();
    var method = this.method;
    var url = this.action;
    $.ajax({
      data: data,
      method: method,
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        $("#center-stage").html(xhr.responseText);
      })
      .done(function(response) {
        var drop = $("#center-stage");
        refreshCookie();
        refreshPage();
        loadResults("/", drop)
        scrollToTop();
        });
  })
  .on("submit", ".password-form", function (e) {
    e.preventDefault();
    var button = $(this).find(".password-button");
    button.text("Loading...");
    var data = $(this).serialize();
    var method = this.method;
    var url = this.action;
    $.ajax({
      data: data,
      method: method,
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        $("#center-stage").html(xhr.responseText);
      })
      .done(function(response) {
        $("#center-stage").html(response);
        scrollToTop();
      });
  })
  .on("click", ".results-close", function(e) {
    e.preventDefault();
    $(this).parents(".results").remove();
  })
  .on("click", ".view-button", function(e) {
    e.preventDefault();
    pushState();
    var collapses = $(this).parents(".results").find($(".results-collapse"));
    collapses.each(function() {
      $(this).collapse("toggle");
    })
    replaceState(this.href);
    $(".view-icon").each(function() {
      var icon = $(this);
      if (icon.hasClass("d-none")) {
        icon.removeClass("d-none");
      }
      else {
        icon.addClass("d-none");
      }
    });
  })
  // BOOTSTRAP COLLAPSES
  .on("show.bs.collapse", ".more-collapse", function(e) {
    $(".more-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".last-played-collapse", function(e) {
    $(".last-played-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".options-collapse", function (e) {
    $(".options-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".results-collapse", function (e) {
    $(".results-collapse.show").collapse("hide");
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
  .on("click", ".showpod-badge", function(e) {
    scrollToTop();
  })
