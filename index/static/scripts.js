"use strict";

var xhr = null;
var timeout = 0;
var last_played = 0;
var charts = 0;

function dateLocalizer() {
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
    var utc = $(this).data("utc");
    var d = utc + tz;
    var d = new Date(d * 1000)
    var dateString =
      ("0" + d.getUTCDate()).slice(-2) + " " +
      ((d.toLocaleString("en-us", {month: "short" }))) + " " +
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
  titleUpdater();
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
  var urls = ["dopebar", "charts", "last-played", "change-password"];
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
  titleUpdater();
  var context = main[0].innerHTML;
  var state = {
    "context": context,
    "url": url,
  };
  history.replaceState(state, "", url);
};
// updates page title
function titleUpdater() {
  // default title
  var title = "dopepod";
  var player = $("#player-wrapper");
  var header = $("#center-stage .results-bar h1");
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
  getResults(["/last-played/", "#last-played", false], true);
};
// abort previous ajax request if url not in urls
function checkForXHR(url) {
  if(xhr != null) {
    var urls = ["dopebar", "charts", "episodes", "last-played", "splash-play"];
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
      else if (url.includes("splash-play")) {
        window.clearInterval(splash_play);
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
      else if (drop.is("#dopebar")) {
        var response = drop.children();
        var theme = response.data("theme")
        response.removeData("theme");
        response.removeAttr("data-theme");
        themeChanger(theme);
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
        drop.find("#episodes-collapse").html(getCircleLoading());
      }
      if (scroll) {
        if (!url.includes("/charts/") && !url.includes("/last-played/") && !url.includes("/splash-play/")) {
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
    playerUnfixer();
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
function playerUnfixer() {
  var x = $("#footer").offset().top;
  var y = $(window).scrollTop() + $(window).height();
  if (x > y) {
    $("#player").addClass("fixed-bottom");
  } else {
    $("#player").removeClass("fixed-bottom");
  }
};
function themeChanger(theme) {
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
        themeChanger(theme);
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
      // TODO if playlist fails
    })
    .done(function (response) {
      if (mode == "play") {
        $("#player").html(response);
        titleUpdater();
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
  titleUpdater();
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
function lastPlayedUpdater() {
  last_played = setInterval(function() {
    if (!$(".last-played .expandable.expanded").length) {
      getResults(["/last-played/", "#last-played", false], true);
    }
  }, 1000 * 60);
};
function chartsUpdater() {
  charts = setInterval(function() {
    getResults(["/charts/", "#charts", false], true);
  }, 1000 * 60 * 60 * 24);
};
function hasTouch() {
  return navigator.maxTouchPoints || navigator.msMaxTouchPoints;
};
function hoverDisabler() {
  if (hasTouch()) {
    $("html").removeClass("no-touch");
  } else {
    $("html").addClass("no-touch");
  }
};
function initSlick() {
  $(".slick").slick({
    autoplay: true,
    prevArrow: "<button type='button' class='btn-dope slick-prev'><i class='fas fa-angle-left' title='Previous'></i></button>",
    nextArrow: "<button type='button' class='btn-dope slick-next'><i class='fas fa-angle-right' title='Next'></i></button>",
  });
}
function initSlickListen() {
  timeout = setTimeout(function() {
    $(".logo").toggleClass("d-none");
    // shuffle all except first (logo)
    var slides = $(".slick-listen .slick-slide").toArray();
    var first = slides.shift();
    for (var i = slides.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var temp = slides[i];
      slides[i] = slides[j];
      slides[j] = temp;
    }
    slides.unshift(first);
    $(".slick-listen").html(slides);
    $(".slick-listen").slick({
      autoplay: true,
      fade: true,
      initialSlide: 1,
      prevArrow: "<button type='button' class='btn-dope slick-prev'><i class='fas fa-angle-left' title='Previous'></i></button>",
      nextArrow: "<button type='button' class='btn-dope slick-next'><i class='fas fa-angle-right' title='Next'></i></button>",
    });
  }, 3000);
};

$(document)
  .ready(function() {
    initSlick();
    initSlickListen();
    scrollToTop();
    refreshCookie();
    scrollUp();
    playerUnfixer();
    scrollSpy();
    lastPlayedUpdater();
    chartsUpdater();
    dateLocalizer();
    hoverDisabler();
    replaceState(window.location.href);
  })
  // SEARCH
  // search when user types into search field (with min "delay" between keypresses)
  .on("submit", ".search-form", function(e) {
    e.preventDefault();
    var url = this.action;
    var form = $(this);
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
  })
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
  .on("click", ".showpod .options-button", function(e) {
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
    $(this).attr('aria-expanded', function (attr) {
      return attr == 'true' ? 'false' : 'true'
    })
    .parents("#player-wrapper").toggleClass("minimize");
  })
  .on("click", ".theme-button[type=submit]", function () {
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
    $(".view-collapse").collapse("toggle");
  })
  // toggle button icon on hover
  .on("mouseenter mouseleave", ".no-touch .order-button, .no-touch .view-button", function () {
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
  })
  .on("show.bs.collapse", ".last-played-collapse", function(e) {
    e.stopPropagation();
    $(".last-played-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".splash-play-collapse", function (e) {
    e.stopPropagation();
    $(".slick-listen").slick("slickPause");
  })
  .on("hide.bs.collapse", ".splash-play-collapse", function (e) {
    e.stopPropagation();
    $(".slick-listen").slick("slickPlay");
  })  
  .on("show.bs.collapse", "#splash-collapse", function () {
    if ($(".slick-listen.slick-initialized").length) {
      $(".slick-listen").slick("slickPlay");
      $(".slick-listen").slick("slickGoTo", 0);
    }
  })
  .on("hide.bs.collapse", "#splash-collapse", function () {
    $(".splash-play-collapse.show").collapse("hide");
    if ($(".slick-listen.slick-initialized").length) {
      $(".slick-listen").slick("slickPause");
    }
  })
  .on("beforeChange", ".slick-listen", function () {
    $("#splash-play-result.expanded").removeClass("expanded");
    $(".splash-play-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".options-collapse", function(e) {
    e.stopPropagation();
    $(".options-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".settings-collapse", function (e) {
    e.stopPropagation();
    $(".settings-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".showpod-collapse", function (e) {
    e.stopPropagation();
    $(".showpod-collapse.show").collapse("hide");
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
    themeChanger(theme);
  })
  .on("click", ".expandable .exp", function () {
    $(".expandable.expanded").removeClass("expanded");
    var button = $(this);
    if (button.attr("aria-expanded") === "true") {
      button.parents(".expandable").addClass("expanded");
    }
  })
  .on("click", "#splash-play-result .exp", function () {
    $("#splash-play-result.expanded").removeClass("expanded");
    var button = $(this);
    if (button.attr("aria-expanded") === "true") {
      button.parents("#splash-play-result").addClass("expanded");
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
  .on("click", ".select", function() {
    $(this).parents(".selectable").toggleClass("selected");
    var buttons = $(".selectable");
    var selected = $(".selectable.selected");
    if (buttons.length == selected.length) {
      $(".select-all").addClass("active");
    }
    else {
      $(".select-all").removeClass("active");
    }
  })
  // selects all subscriptions (and maybe all playlist episodes as well TODO?)
  .on("click", ".select-all", function() {
    var button = $(this);
    if (button.hasClass("active")) {
      $(".selectable").removeClass("selected");
    }
    else {
      $(".selectable").addClass("selected");
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
      titleUpdater();
    }
  })
  .on("blur", function() {
    window.clearInterval(charts);
    window.clearInterval(last_played);
  })
  .on("focus", function() {
    lastPlayedUpdater();
    chartsUpdater();
  })
  .on('resize', function () {
    hoverDisabler();
  });