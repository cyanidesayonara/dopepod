"use strict";

var xhr = null;
var timeout = 0;
var last_played = 0;
var charts = 0;

function localizeDate() {
  var tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  $.ajax({
    data: {
      "tz": tz,
    },
    method: "POST",
    url: "/tz/",
  });

  // local time offset in seconds
  var date = new Date();
  tz = -date.getTimezoneOffset() * 60;

  $(".date").each(function() {
    var d = $(this).data("utc") + tz;
    var d = new Date(d * 1000)
    var dateString =
      ("0" + d.getUTCDate()).slice(-2) + "-" +
      ("0" + (d.getUTCMonth() + 1)).slice(-2) + "-" +
      d.getUTCFullYear() + " " +
      ("0" + d.getUTCHours()).slice(-2) + ":" +
      ("0" + d.getUTCMinutes()).slice(-2);
    $(this).text(dateString);
  });
};
function trackMe(url) {
  _paq.push(['trackPageView', url]);
};
function pushState(url) {
  // return if url in urls
  var urls = ["episodes", "dopebar", "charts", "last-played", "change-password"];
  for (var i = 0; i < urls.length; i++) {
    if (url.includes(urls[i])) {
      return;
    }
  }
  updateTitle();
  var main = $("#main");
  var context = main[0].innerHTML;
  var state = {
    "context": context,
    "url": url,
  };
  history.pushState(state, "", url);
  trackMe(url);  
};
function replaceState(url) {
  url = url.replace("episodes", "showpod");
  // return if url in urls
  var urls = ["settings", "playlist", "subscriptions", "dopebar", "charts", "last-played", "change-password"];
  for (var i = 0; i < urls.length; i++) {
    if (url.includes(urls[i])) {
      return;
    }
  }
  var main = $("#main");
  // ignore these urls, use current url instead
  if (!url || url.includes("unsubscribe")) {
    url = main[0].baseURI;
  }
  updateTitle();
  var context = main[0].innerHTML;
  var state = {
    "context": context,
    "url": url,
  };
  history.replaceState(state, "", url);
};
// updates page title
function updateTitle() {
  // default title
  var title = "dopepod";
  var player = $("#player-wrapper");
  var header = $("#center-stage .results-header h1");
  // if episode is playing
  if (player.length) {
    title = player.find("h1")[0].innerText;
    var episode = player.find(".player-episode")[0].innerText;
    title = "Now playing: " + title + " - " + episode + " | dopepod";
  }
  // if showpod
  else if (header.length) {
    if ($("#center-stage").children().hasClass("showpod")) {
      title = "Listen to episodes of " +  header[0].innerText + " | dopepod";
    }
    else {
      title = header[0].innerText + " | dopepod";
    }
  }
  $("title")[0].innerText = title;
};
// extracts csrftoken (or other data) from cookies
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
};
// these HTTP methods do not require CSRF protection
function csrfSafeMethod(method) {
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};
// for sending csrf token on every ajax POST request
function refreshCookie() {
  var csrftoken = getCookie("csrftoken");
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });
};
// refreshes page on login
function refreshPage() {
  getResults(["/dopebar/", "#dopebar", false], true);
  getResults(["/last-played/", "#last-played", false], true)
};
// abort previous ajax request if url not in urls
function checkForXHR(url) {
  if(xhr != null) {
    var urls = ["dopebar", "charts", "episodes", "last-played"];
    for (var i = 0; i < urls.length; i++) {
      if (url.includes(urls[i])) {
        return;
      }
    }
    xhr.abort();
    xhr = null;
  }
};
// RESULTS
function getResults(args, no_loader, no_push) {
  var url = args[0];
  // sometimes object, sometimes just a string
  var drop = $(args[1]);
  var scroll = args[2];
  var callback = args[3];
  var args = args[4];
  checkForXHR(url);
  if (!no_push) {
    pushState(url);
  }
  xhr = $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
      // if episodes fail, call noshow
      if (url.includes("/episodes/")) {
        podid = url.split("/")[2];
        if (podid) {
          noshow(podid);
        }
      }
      else if (url.includes("last-played")) {
        window.clearInterval(last_played);
      }
      else if (url.includes("charts")) {
        window.clearInterval(charts);
      }
    })
    .done(function(response) {
      drop.html(response);
      // loads episodes
      if (callback) {
        callback(args);
      }
      // if page refresh, apply theme
      else if (drop.is("#dopemenu")) {
        var response = drop.children("#dopebar");
        var theme = response.data("theme")
        response.removeData("theme");
        response.removeAttr("data-theme");
        changeTheme(theme);
      }
      if (scroll) {
        if ((url.includes("/charts/") || url.includes("/last-played/")) && $(window).width() < 992) {
          scrollTo(drop);
        }
      }
      replaceState(url);
    });
  if (!no_loader) {
    if (!drop.children(".loading").length) {
      var results = drop.children(".results");
      if (results.length) {
        results.addClass("loading").children(".results-collapse").html(getCircleLoading());
      }
      else {
        drop.find(".episodes-content").html(getCircleLoading());
      }
      if (scroll) {
        if (!url.includes("/charts/") && !url.includes("/last-played/")) {
          scrollTo(drop);
        }
      }
    }
  }
};
// NOSHOW
function noshow(podid) {
  $.ajax({
    data: {
      "podid": podid,
    },
    method: "POST",
    url: "/noshow/",
  });
};
// SCROLLERS
function scrollSpy() {
  $(window).scroll(function() {
    scrollUp();
    footer();
  });
};
function scrollUp() {
  var scroll = $(window).scrollTop();
  if (scroll > 300) {
    $(".scroll-up").addClass("d-sm-block");
  }
  else {
    $(".scroll-up").removeClass("d-sm-block");
  }
};
function scrollToTop() {
  $("html, body").animate({
    scrollTop: $("body").offset().top
  }, 250);
};
function scrollTo(obj) {
  $("html, body").animate({
    scrollTop: obj.offset().top - 44
  }, 250);
};
// scrolls header text in player if text is wider than bax
function scrollText(box, text) {
  var boxWidth = box.innerWidth();
  var textWidth = text.width();
  if (textWidth > boxWidth) {
    var animSpeed = textWidth * 30;
    $(box)
      .animate({scrollLeft: (textWidth - boxWidth)}, animSpeed)
      .animate({scrollLeft: 0}, animSpeed, function() {
        setTimeout(function() {
          scrollText(box, text);
        }, 1000);
      })
  }
};
function footer() {
  var x = $("#footer").offset().top;
  var y = $(window).scrollTop() + $(window).height();
  if (x > y) {
    $("#player").addClass("fixed-bottom");
  } else {
    $("#player").removeClass("fixed-bottom");
  }
};
function changeTheme(theme) {
  var themes = ["light", "dark", "christmas"];
  for (var i = 0; i < themes.length; i++) {
    if (theme.includes(themes[i])) {
      $("body").removeClass().addClass(theme);
    }
  }
};
function postContact(form) {
  var method = form.method;
  var url = form.action;
  var form = $(form);
  var data = form.serialize();
  var drop = $("#center-stage");
  $.ajax({
    data: data,
    method: method,
    url: url,
  })
    .fail(function (xhr, ajaxOptions, thrownError) {
      $("#center-stage").html(xhr.responseText);
      scrollToTop();
    })
    .done(function (response) {
      drop.html(response);
      scrollToTop();
      replaceState(url);
    });
  drop.children(".results").addClass("loading").children(".results-collapse").html(getCircleLoading());
};
function postSettings(form) {
  var method = form.method;
  var url = form.action;
  var form = $(form);
  var data = form.serialize();
  var theme = form.find("input[name=theme]").val();
  var drop = $("#center-stage");
  $.ajax({
    data: data,
    method: method,
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
      $("#center-stage").html(xhr.responseText);
      scrollToTop();
    })
    .done(function(response) {
      if (theme) {
        changeTheme(theme);
      }
      drop.html(response);
      scrollToTop();
      replaceState(url);
    });
  drop.children(".results").addClass("loading").children(".results-collapse").html(getCircleLoading());
};
function postLogin(form) {
  var method = form.method;
  var url = form.action;
  var form = $(form);
  var data = form.serialize();
  var button = form.find("button[type=submit]");
  var text = button[0].innerText;
  $.ajax({
      data: data,
      method: method,
      url: url,
    })
    // returns errors
    .fail(function(xhr, ajaxOptions, thrownError) {
      $("#center-stage").html(xhr.responseText);
      scrollToTop();
    })
    // returns splashboard
    .done(function(response) {
      $("#center-stage").html(response);
      // if not password reset, refresh page
      if (text === "Login") {
        refreshCookie();
        refreshPage();
      }
      scrollToTop();
    });
    button.html(getButtonLoading());
}
function postSubscriptions(podids, button) {
  clearTimeout(timeout);
  timeout = setTimeout(function() {
    var drop = $("#center-stage");
    $.ajax({
      method: "POST",
      url: "/subscriptions/",
      data: {
        "podids": podids,
      },
    })
    .fail(function(xhr, ajaxOptions, thrownError) {
      drop.html(xhr.responseText);
      replaceState("/");
    })
    .done(function(response) {
      drop.html(response);
      if ($(response).hasClass("showpod")) {
        var url = "/episodes/" + podids + "/";
        drop = ".showpod .results-content";
        getResults([url, drop, false]);
      }
      else {
        scrollTo(drop);
      }
    });
    button.html(getButtonLoading());    
  }, 250);
};
function postPlaylist(data, mode, button) {
  var drop = $("#center-stage");
  var text = button[0].innerHTML;
  var url = "/playlist/";
  $.ajax({
    method: "POST",
    url: url,
    data: data,
  })
    // nothing to continue
    .fail(function(xhr, ajaxOptions, thrownError) {
      button.html(text);
      $("#player").empty();
    })
    .done(function (response) {
      if (mode == "play") {
        $("#player").html(response);
        updateTitle();
        button.html(text);
        // gotta wait a sec here
        setTimeout(function() {
          var box = $("#player-wrapper h1");
          var text = $("#player-wrapper h1 span");
          scrollText(box, text);
        }, 1000);
        if (drop.children(".playlist").length) {
          getResults([url, drop, false]);
        }
      }
      else {
        if (mode == "add") {
          button.text(text);
        }
        if (drop.children(".playlist").length) {
          drop.html(response);
        }
      }
    });
  if (button.is("#player-wrapper")) {
    button.html(getCircleLoading());
  }
  else {
    button.html(getButtonLoading());
  }
};
function playNext() {
  var data = {
    "pos": "1",
    "mode": "play",
  };
  var mode = "play";
  var wrapper = $("#player-wrapper");
  wrapper.children("audio")[0].preload = "none";
  wrapper.empty();
  // wait a sec here
  timeout = setTimeout(function() {
    postPlaylist(data, mode, wrapper);
  }, 500);
};
function closePlayer() {
  var player = $("#player");
  player.find("audio")[0].preload = "none";
  player.empty();
  updateTitle();
};
// replaces spaces/&s with +, removes unwanted chars
function cleanString(q) {
  q = q.replace(/&+/g, "+");
  q = q.replace(/\s+/g, "+");
  q = q.replace(/([^a-zA-Z0-9\u0080-\uFFFF +']+)/gi, "");
  return q.toLowerCase();
};
function getButtonLoading() {
  return $(".button-loading").first().clone();
};
function getCircleLoading() {
  return $(".circle-loading").first().clone();
};
function updateLastPlayed() {
  last_played = setInterval(function() {
    getResults(["/last-played/", "#last-played", false], true);
  }, 1000 * 60);
};
function updateCharts() {
  charts = setInterval(function() {
    getResults(["/charts/", "#charts", false], true);
  }, 1000 * 60 * 60 * 24);
};

$(document)
  .ready(function() {
    $(".slick").slick({
      autoplay: true,
      adaptiveHeight: true,
      prevArrow: "<button type='button' class='btn-dope slick-prev'><i class='fas fa-angle-left' title='Previous'></i></button>",
      nextArrow: "<button type='button' class='btn-dope slick-next'><i class='fas fa-angle-right' title='Next'></i></button>",
    });
    scrollToTop();
    refreshCookie();
    scrollUp();
    footer();
    scrollSpy();
    updateLastPlayed();
    updateCharts();
    localizeDate();
    replaceState(window.location.href);
  })
  // SEARCH
  // search when user types into search field (with min "delay" between keypresses)
  .on("submit", ".search-form", function(e) {
    e.preventDefault();
    var url = this.action;
    var form = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var q = form.children(".q").val();
      if (q) {
        q = cleanString(q);
        var drop = $("#center-stage");
        if (!(drop.children(".results").data("q") == q)) {
          url = url + "?q=" + q;
          getResults([url, drop, true]);
        }
        else {
          scrollTo(drop);
        }
      }
    }, 250);
  })
  // search when user clicks buttons
  .on("click", ".options-button", function(e) {
    e.preventDefault();
    var url = this.href;
    var button = $(this);
    var view = button.parents(".results").data("view");
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      if (view) {
        if (url.includes("view")) {
          url = url.substring(0, url.indexOf("view")) + "view=" + view;
        } else {
          url += "&view=" + view;
        }
      }
      var drop = button.parents(".results").parent();
      getResults([url, drop, true]);
    }, 250);
  })
  // search when user clicks buttons
  .on("click", ".showpod .pages-buttons .options-button", function(e) {
    e.preventDefault();
    // redirect to episodes
    var url = this.href.replace("showpod", "episodes");
    var button = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = button.parents(".results-content");
      getResults([url, drop, false]);
    }, 250);
  })
  // NAVIGATION
  .on("click", ".showpod-link", function(e) {
    e.preventDefault();
    var url = this.href;
    var button = $(this);
    var podid = button.data("podid");
    var drop = $("#center-stage");
    drop.find(".results-collapse").collapse("show");
    if (!(drop.children(".results").data("podid") == podid)) {
      var scroll = false;
      var args = ["/episodes/" + podid + "/", ".showpod .results-content", false];
      getResults([url, drop, true, getResults, args]);
    }
    else {
      scrollTo(drop);
    }
  })  
  // LOGIN & SIGNUP
  // show splash / dashboard / login / register / password reset
  .on("click", ".login-link, .signup-link, .password-link, .index-link", function(e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    var link = $(this);
    drop.find(".results-collapse").collapse("show");
    if (!drop.children(".splash").length && !drop.children(".dashboard").length) {
      getResults([url, drop, true]);
    }
    else {
      if (link.hasClass("login-link")) {
        drop.find("#login-collapse").collapse("show");
      }
      else if (link.hasClass("signup-link")) {
        drop.find("#signup-collapse").collapse("show");
      }
      else if (link.hasClass("password-link")) {
        drop.find("#password-collapse").collapse("show");
      }
      else {
        drop.find("#splash-collapse").collapse("show");
      }
      if (link.hasClass("collapsed")) {
        drop.find("#splash-collapse").collapse("show");
      }
      scrollTo(drop);
    }
  })
  .on("click", ".browse-link", function(e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    drop.find(".results-collapse").collapse("show");
    if (!drop.children(".list").length && !drop.children(".grid").length) {
      getResults([url, drop, true]);
    }
    else {
      if (window.location.href.includes("?")) {
        getResults([url, drop, true]);
      }
      else {
        scrollTo(drop);
      }
    }
  })
  .on("click", ".subscriptions-link", function(e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    drop.find(".results-collapse").collapse("show");
    if (!drop.children(".subscriptions").length) {
      getResults([url, drop, true]);
    }
    else {
      scrollTo(drop);
    }
  })
  .on("click", ".settings-link", function(e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    drop.find(".results-collapse").collapse("show");
    if (!drop.children(".settings").length) {
      getResults([url, drop, true]);
    }
    else {
      scrollTo(drop);      
    }
  })
  .on("click", ".playlist-link", function(e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    drop.find(".results-collapse").collapse("show");
    if (!drop.children(".playlist").length) {
      getResults([url, drop, true]);
    }
    else {
      scrollTo(drop);
    }
  })
  .on("click", ".charts-link", function(e) {
    e.preventDefault();
    scrollTo($("#charts"));
  })
  .on("click", ".last-played-link", function(e) {
    e.preventDefault();
    scrollTo($("#last-played"));
  })
  .on("click", ".privacy-link", function (e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    drop.find(".results-collapse").collapse("show");
    if (!drop.children(".privacy").length) {
      getResults([url, drop, true]);
    } else {
      scrollTo(drop);
    }
  })
  .on("click", ".terms-link", function (e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    drop.find(".results-collapse").collapse("show");
    if (!drop.children(".terms").length) {
      getResults([url, drop, true]);
    } else {
      scrollTo(drop);
    }
  })
  .on("click", ".api-link", function (e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    drop.find(".results-collapse").collapse("show");
    if (!drop.children(".api").length) {
      getResults([url, drop, true]);
    } else {
      scrollTo(drop);
    }
  })
  .on("click", ".contact-link", function (e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    drop.find(".results-collapse").collapse("show");
    if (!drop.children(".contact").length) {
      getResults([url, drop, true]);
    } else {
      scrollTo(drop);
    }
  })
  // sub or unsub
  .on("submit", ".subscriptions-form", function(e) {
    e.preventDefault();
    var form = $(this);
    var button = form.children("button[type=submit]");
    var podids = form.children("input[name=podid]").val();
    if (!podids) {
      podids = [];
      podids[0] = form.children("input[name^=podids]").val();
    }
    if (podids) {
      postSubscriptions(podids, button);
    }
  })
  // unsubscribe one or more podcasts
  // POST ajax request, data is array of podids
  .on("click", ".unsubscribe-button", function(e) {
    e.preventDefault();
    var button = $(this);
    var selected = button.parents(".results-content").find(".grid-result.selected");
    if (selected.length) {
      // array of all selected podids
      var podids = [];
      selected.each(function (i, sub) {
        podids[i] = $(sub).data("podid");
      })
    }
    // if nothing selected, do nothing
    else {
      return;
    }
    if (podids) {
      postSubscriptions(podids, button);
    }
  })
  // playlist - play, add, move, or delete episode
  .on("submit", ".playlist-form", function(e) {
    e.preventDefault();
    var form = $(this);
    if (!form.find(".button-loading").length) {
      clearTimeout(timeout);
      timeout = setTimeout(function () {
        var data = form.serialize();
        var mode = form.children("input[name=mode]").val();
        var button = form.children("button[type=submit]");
        postPlaylist(data, mode, button);
      }, 250);
    }
  })
  // close player
  .on("click", ".player-close", function(e) {
    e.preventDefault();
    closePlayer();
  })
  // minimize player
  .on("click", ".player-minimize", function(e) {
    e.preventDefault();
    $("#player-collapse").collapse("hide");
    $("#player-close-collapse").collapse("hide");
    $(this).attr('aria-expanded', function (i, attr) {
      return attr == 'true' ? 'false' : 'true'
    })
    .parents("#player-wrapper").toggleClass("minimize");
  })
  .on("click", ".theme-button[type=submit]", function (e) {
    var theme = this.innerText.toLowerCase();
    $(this).siblings("input[name=theme]").val(theme);
  })
  .on("submit", ".contact-form", function (e) {
    e.preventDefault();
    postContact(this);
  })  
  // save settings, apply theme
  .on("submit", ".settings-form", function(e) {
    e.preventDefault();
    postSettings(this);
  })
  // login or signup and refresh page/send password link
  .on("submit", ".login-form, .signup-form, .password-form, .password-reset-form", function(e) {
    e.preventDefault();
    postLogin(this);
  })
  // toggle view icon & view collapse on click
  .on("click", ".view-button", function(e) {
    e.preventDefault();
    var button = $(this);
    var view = button.children(".d-none").data("view");
    button.children().toggleClass("d-none");
    button.parents(".results").attr("data-view", view)
    button.parent().parent().siblings(".view-collapse")
      .each(function() {
        $(this).collapse("toggle");
      });
  })
  // toggle button icon on hover
  .on("mouseenter mouseleave", ".order-button, .view-button, .provider-button", function () {
    $(this).children().toggleClass("d-none");
  })
  // BOOTSTRAP COLLAPSES
  .on("show.bs.collapse", ".login-collapse", function(e) {
    e.stopPropagation();
    $(".login-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".more-collapse", function(e) {
    e.stopPropagation();
    $(".more-collapse.show").collapse("hide");
    var obj = $(this).parents("tr").prev();
    timeout = setTimeout(function () {
      if ($(window).width() < 992) {
        scrollTo(obj);
      }
    }, 250);
  })
  .on("show.bs.collapse", ".last-played-collapse", function(e) {
    e.stopPropagation();
    $(".last-played-collapse.show").collapse("hide");
    var obj = $(this).parent();
    timeout = setTimeout(function () {
      scrollTo(obj);
    }, 250);
  })
  .on("show.bs.collapse", ".options-collapse", function(e) {
    e.stopPropagation();
    $(".options-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".settings-collapse", function (e) {
    e.stopPropagation();
    $(".settings-collapse.show").collapse("hide");
  })
  .on("click", ".episodes-button, .reviews-button", function(e) {
    e.stopPropagation();
    $(".showpod-collapse").collapse("toggle");
  })
  .on("click", ".select-theme", function(e) {
    e.preventDefault();
    var theme = $("body").attr("class");
    if (theme == "light") {
      theme  = "dark";
    } else if (theme == "dark") {
      theme = "christmas";
    } else if (theme == "christmas") {
      theme = "light";
    }
    changeTheme(theme);
  })
  .on("click", ".dope-toggle", function () {
    $(".last-played-result.expanded").removeClass("expanded");
    var button = $(this);
    if (button.attr("aria-expanded") === "true") {
      button.parent().addClass("expanded");
    }
  })  
  // removes focus from buttons when clicked
  .on("click", ".btn-dope, .dope-link, .dope-toggle, .episode-header, .search-button", function() {
    $(this).blur();
  })
  // empties search field when link or button is clicked
  .on("click", "a, button:not(.search-button)", function() {
    $(".q").val("");
  })
  // deletes error text (after delay) when clicking anywhere
  .on("click", "body", function() {
    $(".errors").delay(2000).fadeOut("slow", function() {
      $(this).remove();
    });
  })
  // hides dopebar-collapse...
  .on("click", "body, .dope-link, .search-button", function() {
    $("#dopebar-collapse.show").collapse("hide");
  })
  // ...except when dopebar-collapose is clicked
  .on("click", "#dopebar", function(e) {
    e.stopPropagation();
  })
  .on("click", ".scroll-up", function() {
    scrollToTop();
  })
  .on("click", ".select-subscription", function() {
    var box = $(this).parents(".grid-result").toggleClass("selected");
    var buttons = box.parents(".results").find(".grid-result");
    var selected = box.parents(".results").find(".selected");
    if (buttons.length == selected.length) {
      $(".select-all-button").addClass("active");
    }
    else {
      $(".select-all-button").removeClass("active");
    }
  })
  // selects all subscriptions (and maybe all playlist episodes as well TODO?)
  .on("click", ".select-all-button", function() {
    var button = $(this);
    if (button.hasClass("active")) {
      button.parent().parent().siblings().find(".grid-result").removeClass("selected");
    }
    else {
      button.parent().parent().siblings().find(".grid-result").addClass("selected");
    }
    button.toggleClass("active");
  })
  .on("click", ".cookie-banner-close", function() {
    $("#player").empty();
  });

$(window)
  .on("popstate", function(e) {
    var state = e.originalEvent.state;
    if (state) {
      // if url in urls, reload results (and don't push)
      var url = state.url;
      var urls = ["settings", "playlist", "subscriptions"];
      for (var i = 0; i < urls.length; i++) {
        if (url.includes(urls[i])) {
          var drop = $("#center-stage");
          getResults([url, drop, false], false, true);
          return;
        }
      }
      $("#main").html(state.context);
      updateTitle();
    }
  })
  .on("blur", function() {
    window.clearInterval(charts);
    window.clearInterval(last_played);
  })
  .on("focus", function() {
    updateLastPlayed();
    updateCharts();
  });