// after page loads
$(document)
  .ready(function() {
    xhr = null;
    timeout = 0;
    refreshCookie();
    collapseCollapses();
    addIcons();
    navbarUnFixer();
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
  var view_buttons = $(".view-button");
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
  $("#multibar-options-collapse").collapse("hide");
}

function scrollSpy() {
  $(window).scroll(function () {
    navbarUnFixer();
  })
}

function navbarUnFixer() {
  var scroll = $(window).scrollTop();
  var navbar = $("#navbar");
  if (scroll > 499) {
    navbar.css("top", "-50px");
    var el = $("#multibar-c");
    moveLogo(el);
  }
  else if (scroll < 457) {
    navbar.css("top", "0");
    var el = $("#navbar-c");
    moveLogo(el);
  }
  else {
    var top = (456 - scroll) + "px";
    navbar.css("top", top);
  }
}

function moveLogo(el) {
  if (el.length && !el.children().length) {
    var logo = $(".logo-wrapper");
    logo.children().each(function() {
      $(this).addClass("logo-final");
    })
    el.html(logo);
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
    url: "/multibar/",
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
    })
    .done(function(response) {
      $("#episodes").empty();
      $("#results").empty();
      var drop = $("#charts");
      loadResults("/charts/", drop);
      $("#multibar-drop").html(response);
    });
}

function checkForXHR() {
  if(xhr != null) {
    xhr.abort();
    xhr = null;
  }
}
function clearSearch() {
  $("#q").val("");
}

// LOADERS
function loadEpisodes(podid) {
  $("#episodes").load("/static/loading.html");
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
        $("#episodes").html(response);
        var url = $("#main-wrapper")[0].baseURI;
        replaceState(url);
      }
    });
}
function loadResults(url, drop) {
  checkForXHR();
  $("#episodes").empty();
  $(drop).load("/static/loading.html");
  xhr = $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
  })
    .done(function(response) {
      drop.html(response);
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
    scrollTop: 500
  }, 250);
}
function scrollText(box, text) {
  var boxWidth = box.width();
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
      var url = el[0].action;
      var drop = $("#search");
      var q = $("#q").val();
      if (q) {
        url = url + '?q=' + q;
        pushState();
        loadResults(url, drop);
        $("#browse-collapse").collapse("hide");
        $("#multibar-options-collapse").collapse("hide");
        scrollToMultibar()
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
      if (q) {
        url = url + '?q=' + q;
        pushState();
        loadResults(url, drop);
        $("#browse-collapse").collapse("hide");
        $("#multibar-options-collapse").collapse("hide");
        scrollToMultibar();
      }
    }, 250);
  })
  .on("click", ".alphabet-buttons a", function(e) {
    e.preventDefault();
    var el = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = el[0].href;
      var drop = $("#search");
      pushState();
      loadResults(url, drop);
      clearSearch();
      $("#browse-collapse").collapse("hide");
      $("#multibar-options-collapse").collapse("hide");
      scrollToMultibar();
    }, 250);
  })
  // search when user clicks buttons
  .on("click", ".page-buttons a, .genre-buttons a, .language-buttons a", function(e) {
    e.preventDefault();
    var el = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = el[0].href;
      var drop = $(el.parents(".results").parent()[0]);
      pushState();
      loadResults(url, drop);
      clearSearch();
      $("#browse-collapse").collapse("hide");
      $("#multibar-options-collapse").collapse("hide");
      if (drop[0].id != "charts") {
        scrollToMultibar()
      }
    }, 250);
  })
  .on("click", ".genre_rank a", function(e) {
    e.preventDefault();
    var el = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = el[0].href;
      var drop = $("#charts");
      pushState();
      loadResults(url, drop);
      clearSearch();
      $("#browse-collapse").collapse("hide");
      $("#multibar-options-collapse").collapse("hide");
      scrollToMultibar()
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
      pushState();
      loadResults(url, drop);
      clearSearch();
      $("#browse-collapse").collapse("hide");
      $("#multibar-options-collapse").collapse("hide");
      loadEpisodes(podid);
      scrollToTop();
    }, 250);
  })
  .on("click", ".index-link", function(e) {
    e.preventDefault();
    var url = this.href;
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = $("#center-stage");
      pushState();
      loadResults(url, drop);
      clearSearch();
      $("#browse-collapse").collapse("hide");
      $("#multibar-options-collapse").collapse("hide");
      $("#episodes").empty();
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
      clearSearch();
      $("#episodes").empty();
      $("#browse-collapse").collapse("show");
      $("#multibar-options-collapse").collapse("hide");
      scrollToMultibar();
    }, 250);
  })
  .on("click", ".charts-link", function(e) {
    e.preventDefault();
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = $("#search");
      $("#search").empty();
      $("#episodes").empty();
      $("#browse-collapse").collapse("hide");
      $("#multibar-options-collapse").collapse("hide");
      scrollToMultibar();
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
      clearSearch();
      $("#episodes").empty();
      $("#browse-collapse").collapse("hide");
      $("#multibar-options-collapse").collapse("hide");
      scrollToMultibar();
    }, 250);
  })
  // open settings
  .on("click", ".settings-link", function(e) {
    e.preventDefault();
    var url = this.href;
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = $("#center-stage");
      pushState();
      $("#browse-collapse").collapse("hide");
      $("#multibar-options-collapse").collapse("hide");
      clearSearch();
      loadResults(url, drop);
      $("#episodes").empty();
      scrollToTop();
    }, 250);
  })
  // FORMS
  .on("submit", "#settings-form", function (e) {
    e.preventDefault();
    var button = $(this).find("#settings-save");
    button.text("Saving...");
    var data = $(this).serialize();
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
        console.log(url, drop)
        loadResults(url, drop);
        loadEpisodes(podid);
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
        player.html(response);
        var img = player.find("#player-image");
        $("#player-image-drop").html(img).removeClass("d-none");
        $("#player-logo").addClass("d-none");
        updateTitle();
        var box = $("#player-top");
        var text = $("#player-title");
        scrollText(box, text);
      });
  })
  // close player
  .on("click", "#player-close", function(e) {
    e.preventDefault();
    $("#audio-el").preload="none";
    $("#player-drop").empty();
    $("#player-image-drop").html("").addClass("d-none");
    $("#player-logo").removeClass("d-none");
    updateTitle();
  })
  .on("click", "#player-minimize", function(e) {
    e.preventDefault();
    if ($("#player-bottom").hasClass("d-none")) {
      $("#player-bottom").removeClass("d-none");
    }
    else {
      $("#player-bottom").addClass("d-none");
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
    clearSearch();
    $("#browse-collapse").collapse("hide");
    $("#multibar-options-collapse").collapse("hide");
    $("#episodes").empty();
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
  .on("click", "#show-episodes", function(e) {
    e.preventDefault();
    var el = $("#results-collapse-episodes");
    if (el.length) {
      if (!el.hasClass("show")) {
        el.collapse('show');
      }
    }
    else {
      var podid = $("#showpod-c").data("podid");
      loadEpisodes(podid);
    }
    scrollToMultibar();
  })
  .on("click", ".results-close", function(e) {
    e.preventDefault();
    $(this).parents(".results").remove();
  })
  .on("click", ".view-button", function(e) {
    e.preventDefault();
    var collapses = $(this).parents(".results").find($(".results-collapse"));
    collapses.each(function() {
      $(this).collapse("toggle");
    })
    $(this).find(".view-icon").each(function() {
      var icon = $(this);
      if (icon.hasClass("d-none")) {
        icon.removeClass("d-none")
      }
      else {
        icon.addClass("d-none")
      }
    });
  })
  // BOOTSTRAP COLLAPSES
  .on("show.bs.collapse", ".more-collapse", function(e) {
      $(".more-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".options-collapse", function (e) {
      $(".options-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".results-collapse", function (e) {
      $(".results-collapse.show").collapse("hide");
  })
   .on("click", ".view-button, .results-minimize", function(e) {
     $(this).parents(".results").find(".options-collapse.show").collapse("hide");
   })
  .on("click", ".results-header .btn-dope.toggle, .view-button", function(e) {
    $(this).parents(".results").find(".results-wrapper.collapse").collapse("show");
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
  .on("click", "#navbar .multibar-options-toggle", function(e) {
    scrollToMultibar();
  })
