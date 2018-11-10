"use strict";

var xhr = null;
var timeout = 0;
var previous = 0;
var charts = 0;

refreshCookie();
dateLocalizer();
lazyload();
hoverDisabler();

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
  var urls = ["episodes", "dopebar", "subscriptions", "playlist", "charts", "previous", "change-password"];
  for (var i = 0; i < urls.length; i++) {
    if (url.includes(urls[i])) {
      return;
    }
  }
  titleUpdater();
  var main = $("#center-stage");
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
  var urls = ["dopebar", "subscriptions", "playlist", "charts", "previous", "change-password"];
  for (var i = 0; i < urls.length; i++) {
    if (url.includes(urls[i])) {
      return;
    }
  }
  var main = $("#center-stage");
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
  getResults(["/dopebar/", "#dopebar-wrapper", false], true);
  getResults(["/previous/", "#previous", false], true);
  getResults(["/charts/", "#charts", false], true);
  getResults(["/subscriptions/", "#subscriptions", false], true);
  getResults(["/playlist/", "#playlist", false], true);
};
// abort previous ajax request if url not in urls
function checkForXHR(url) {
  if(xhr != null) {
    var urls = ["dopebar", "charts", "episodes", "previous", "subscriptions", "playlist"];
    for (var i = 0; i < urls.length; i++) {
      if (url.includes(urls[i])) {
        return;
      }
    }
    xhr.abort();
    xhr = null;
  }
};
function enableLoader(drop, url) {
  if (drop.is("#player")) {
    drop.find(".player-content").addClass("blurred");
  } else {
    drop.children(":not(.loader)").addClass("blurred");
  }
  var loader = drop.find(".loader:last");
  loader.fadeIn("slow");
  loader.filter(".reload-button").attr("href", url);
};
function disableLoader(drop) {
  drop.children(":not(.loader)").removeClass("blurred");
  var loader = drop.find(".loader:last");
  loader.fadeOut("slow");
  loader.filter(".reload-button").attr("href", url);
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
  if (!no_loader) {
    drop.find(".results-collapse:not(.show)").collapse("show");
    enableLoader(drop, url);
    if (scroll) {
      if (!url.includes("/charts/") && !url.includes("/previous/")) {
        scrollTo(drop);
      }
    }
  }
  xhr = $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
      // if episodes fail, call noshow
      if (url.includes("/episodes/") && thrownError != "abort") {
        podid = url.split("/")[2];
        if (podid) {
          noshow(podid);
        }
      }
      else if (url.includes("previous")) {
        window.clearInterval(previous);
      }
      else if (url.includes("charts")) {
        window.clearInterval(charts);
      }
    })
    .done(function(response) {
      drop.html(response);
      lazyload();
      // loads episodes
      if (callback) {
        callback(args);
      }
      // if page refresh, apply theme
      else if (drop.is("#dopebar-wrapper")) {
        var response = drop.children();
        var theme = response.data("theme");
        response.removeData("theme");
        response.removeAttr("data-theme");
        themeChanger(theme);
      }
      if (scroll) {
        if ((url.includes("/charts/") || url.includes("/previous/")) && $(window).width() < 992) {
          scrollTo(drop);
        }
      }
      replaceState(url);
    });
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
// SCROLLIES
function scrollSpy() {
  scrollUp();
  playerUnfixer();
  columnFixer();
};
function scrollUp() {
  var scroll = $(window).scrollTop();
  if (scroll > 300) {
    $("#scroll-up").addClass("d-inline-block");
  }
  else {
    $("#scroll-up").removeClass("d-inline-block");
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
function columnFixer() {
  $("#subscriptions, #playlist").stick_in_parent({
    offset_top: 44
  });
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
      drop.html(xhr.responseText);
      scrollToTop();
    })
    .done(function (response) {
      drop.html(response);
      scrollToTop();
      replaceState(url);
    });
  enableLoader(drop, url);
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
      drop.html(xhr.responseText);
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
  enableLoader(drop, url);
};
function postLogin(form) {
  var method = form.method;
  var url = form.action;
  var form = $(form);
  var data = form.serialize();
  var drop = $("#center-stage");
  form.find("button[type=submit].btn-dope").html(getButtonLoading());
  $.ajax({
      data: data,
      method: method,
      url: url,
    })
    // returns errors
    .fail(function(xhr, ajaxOptions, thrownError) {
      drop.html(xhr.responseText);
      scrollToTop();
    })
    // returns splashboard
    .done(function(response) {
      drop.html(response);
      scrollToTop();
      // if not password reset, refresh page
      if (form.hasClass("login-form") || form.hasClass("tryout-form")) {
        refreshCookie();
        refreshPage();
      }
    });
};
function postSubscriptions(podid, button) {
  clearTimeout(timeout);
  timeout = setTimeout(function() {
    var drop = $("#subscriptions");
    $.ajax({
      method: "POST",
      url: "/subscriptions/",
      data: {
        "podid": podid,
      },
    })
    .fail(function(xhr, ajaxOptions, thrownError) {
    })
    .done(function(response) {
      if (drop.children().length) {
        drop.find(".results-collapse").html($(response).find(".results-collapse").children());
      } else {
        drop.html(response);
      }
      drop.trigger("sticky_kit:recalc");
      var current_podid = $(".results.showpod").data("podid");
      if (podid == current_podid) {
        var args = ["/episodes/" + podid + "/", ".showpod #episodes-content", false];
        getResults(["/showpod/" + podid, "#center-stage", false, getResults, args], false, true); 
      }
      getResults(["/charts/", "#charts", false]);
    });
    button.html(getButtonLoading());    
  }, 250);
};
function postPlaylist(data, mode, button, pos) {
  var drop = $("#playlist");
  try {
    var text = button[0].innerHTML;
  } catch (e) {
  }
  var url = "/playlist/";
  if (mode == "play") {
    var wrapper = $("#player-wrapper");
    if (wrapper.length) {
      wrapper.removeClass("minimize");
      wrapper.find("audio")[0].preload = "none";
      enableLoader($("#player"));
    }
  }
  $.ajax({
    method: "POST",
    url: url,
    data: data,
  })
    // nothing to continue
    .fail(function(xhr, ajaxOptions, thrownError) {
      try {
        button.html(text);
      } catch (e) {
      }
      $("#player").empty();
      // TODO if playlist fails
    })
    .done(function (response) {
      if (mode == "play") {
        var player = $("#player");
        player.html(response);
        titleUpdater();
        try {
          button.html(text);
        } catch (e) {
        }
        // gotta wait a sec here
        setTimeout(function() {
          var box = player.find("h1");
          var text = player.find("h1 span");
          scrollText(box, text);
        }, 1000);
        if (pos && drop.children().length) {
          getResults([url, drop, false]);
        }
      }
      else {
        if (mode == "add") {
          button.html(text);
        }
        drop.find(".results-collapse").html($(response).find(".results-collapse").children());
        lazyload();
        drop.trigger("sticky_kit:recalc");
      }
      drop.trigger("sticky_kit:recalc");
    });
  try {
    button.html(getButtonLoading());
  } catch (e) {
  }
};
function playNext() {
  var mode = "play";
  var pos = "1";
  var data = {
    "mode": mode,
    "pos": pos,
  };
  var button = undefined;
  postPlaylist(data, mode, button, pos);
}
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
function previousUpdater() {
  previous = setInterval(function() {
    if (!$(".previous .expandable.expanded").length) {
      getResults(["/previous/", "#previous", false], true);
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
function initPopular() {
  $(".popular-carousel")
    .slick({
      autoplay: true,
      infinite: true,
      lazyload: "ondemand",
      prevArrow: "<button type='button' class='btn-dope slick-prev' title='Previous'><span><i class='fas fa-angle-left'></i></span></button>",
      nextArrow: "<button type='button' class='btn-dope slick-next' title='Next'><span><i class='fas fa-angle-right'></i></span></button>",
    })
    .show()
    .slick("refresh");
};
function initListen() {
  $(".logo").toggleClass("d-none");
  // shuffle all except first (logo)
  var slides = $(".listen-carousel>*").toArray();
  var first = slides.shift();
  for (var i = slides.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var temp = slides[i];
    slides[i] = slides[j];
    slides[j] = temp;
  }
  slides.unshift(first);
  $(".listen-carousel")
    .html(slides)
    .slick({
      autoplay: true,
      fade: true,
      initialSlide: 1,
      lazyLoad: "ondemand",
      prevArrow: "<button type='button' class='btn-dope active slick-prev' title='Previous'><span><i class='fas fa-angle-left'></i></span></button>",
      nextArrow: "<button type='button' class='btn-dope active slick-next' title='Next'><span><i class='fas fa-angle-right'></i></span></button>",
    })
    .show()
    .slick("refresh");
};
function removeErrors() {
  $(".errors").remove();
};
function lazyload() {
  var myLazyLoad = new LazyLoad({
    elements_selector: ".lazyload"
  });
};
function toggleButtons(buttons) {
  // change icons on both buttons
  buttons.each(function() {
    $(this).children().slice(-2).toggleClass("d-none");
  });
};
function togglePopular() {
  var carousel = $(".popular-carousel");
  var index = carousel.slick("slickCurrentSlide");
  var cut = 16;
  if (index >= cut) {
    carousel.slick("slickGoTo", 0);
  } else if (index < cut) {
    carousel.slick("slickGoTo", cut);
  }
};

$(document)
  .ready(function() {
    replaceState(window.location.href);
    scrollSpy();
    initListen();
    initPopular();
    previousUpdater();
    chartsUpdater();
  })
  .scroll(function() {
    scrollSpy();
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
  .on("click", ".reload-button", function(e) {
    e.preventDefault();
    var url = this.href;
    var button = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = button.parents(".loader").parent();
      if (drop.is("episodes-content")) {
        url = url.replace("showpod", "episodes");
        getResults([url, drop, false]);
      } else if (drop.length) {
        var podid = drop.children(".results.showpod").data("podid");
        if (podid) {
          var args = ["/episodes/" + podid + "/", ".showpod #episodes-content", false];
          getResults([url, drop, false, getResults, args]);          
        } else {
          getResults([url, drop, false]);
        }
      }
    }, 250);
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
      var drop = button.parents("#episodes-content");
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
    if (!(drop.children(".results").data("podid") == podid)) {
      var args = ["/episodes/" + podid + "/", ".showpod #episodes-content", false];
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
    var drop = $("#subscriptions");
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
    var drop = $("#playlist");
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
  .on("click", ".previous-link", function(e) {
    e.preventDefault();
    scrollTo($("#previous"));
  })
  .on("click", ".privacy-link", function(e) {
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
  .on("click", ".terms-link", function(e) {
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
  .on("click", ".api-link", function(e) {
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
  .on("click", ".contact-link", function(e) {
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
    var podid = form.children("input[name^=podid]").val();
    if (podid) {
      postSubscriptions(podid, button);
    }
  })
  // unsubscribe one or more podcasts
  // POST ajax request, data is array of podids
  .on("click", ".unsubscribe-button", function(e) {
    e.preventDefault();
    e.stopPropagation();
    var button = $(this);
    var selected = button.parents(".results-collapse").find(".selectable.selected");
    if (selected.length) {
      if (button.hasClass("exp")) {
        console.log("asasd")
        return
      }
      // array of all selected podid
      var podid = [];
      selected.each(function(i, subscription) {
        podid[i] = $(subscription).data("podid");
      })
    }
    // if nothing selected, do nothing
    else {
      return;
    }
    if (podid) {
      postSubscriptions(podid, button);
    }
  })
  // playlist - play, add, move, or delete episode
  .on("submit", ".playlist-form", function(e) {
    e.preventDefault();
    var form = $(this);
    if (!form.find(".button-loading").length) {
      clearTimeout(timeout);
      timeout = setTimeout(function() {
        var data = form.serialize();
        var mode = form.children("input[name=mode]").val();
        var pos = form.children("input[name=pos]").val();
        var button = form.children("button[type=submit]");
        postPlaylist(data, mode, button, pos);
      }, 250);
    }
  })
  // minimize player
  .on("click", ".player-minimize", function(e) {
    e.preventDefault();
    $("#player-collapse").collapse("hide");
    $("#confirm-collapse-player").collapse("hide");
    $(this).attr("aria-expanded", function(i, attr) {
      return attr == "true" ? "false" : "true";
    })
    .parents("#player-wrapper").toggleClass("minimize");
  })
  .on("click", ".theme-button[type=submit]", function() {
    var theme = $(this).children().text().toLowerCase();
    $(this).siblings("input[name=theme]").val(theme);
  })
  .on("submit", ".contact-form", function(e) {
    e.preventDefault();
    postContact(this);
  })  
  // save settings, apply theme
  .on("submit", ".settings-form", function(e) {
    e.preventDefault();
    postSettings(this);
  })
  .on("submit", ".convert-form", function(e) {
    e.preventDefault();
    alert("Oops, this doesn't actually work yet. Sorry!");
  })  
  // login or signup and refresh page/send password link
  .on("submit", ".tryout-form, .login-form, .signup-form, .password-form, .password-reset-form", function(e) {
    e.preventDefault();
    postLogin(this);
  })
  .on("click", ".showpod-button", function (e) {
    e.preventDefault();

    // if button not pressed
    if ($(this).children(".d-none.active").length) {
      $(".showpod-content").toggleClass("d-none");
      toggleButtons($(".showpod-button"));
    }
    scrollTo($(".showpod-content:not(.d-none)"));
  })
  .on("click", ".popular-button", function(e) {
    e.preventDefault();

    // if button not pressed
    if ($(this).children(".d-none.active").length) {
      togglePopular();
    }
  })
  // toggle view icon & view collapse on click
  .on("click", ".view-button", function(e) {
    e.preventDefault();
    var icons = $(this).children().slice(-2);
    var view = icons.filter(".d-none").data("view");
    icons.parents(".results").attr("data-view", view)
    icons.toggleClass("d-none");
    $(".view-collapse").collapse("toggle");
  })
  // BOOTSTRAP COLLAPSES
  .on("show.bs.collapse", ".login-collapse", function(e) {
    e.stopPropagation();
    $(".login-collapse.show").collapse("hide");
    removeErrors();
  })
  .on("show.bs.collapse", ".more-collapse", function(e) {
    e.stopPropagation();
    $(this).parents(".results").find(".more-collapse.show").collapse("hide");
  })
  .on("shown.bs.collapse hidden.bs.collapse", "#playlist .more-collapse", function (e) {
    e.stopPropagation();
    $(this).parents(".results").trigger("sticky_kit:recalc");
  })
  .on("show.bs.collapse", ".previous-collapse", function(e) {
    e.stopPropagation();
    $(".previous-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".listen-collapse", function(e) {
    e.stopPropagation();
    $(".listen-carousel").slick("slickPause");
  })
  .on("hide.bs.collapse", ".listen-collapse", function(e) {
    e.stopPropagation();
    $(".listen-carousel").slick("slickPlay");
  })  
  .on("show.bs.collapse", "#splash-collapse", function() {
    if ($(".listen-carousel.slick-initialized").length) {
      $(".listen-carousel").slick("slickPlay");
      $(".listen-carousel").slick("slickGoTo", 0);
    }
  })
  .on("hide.bs.collapse", "#splash-collapse", function() {
    $(".listen-collapse.show").collapse("hide");
    if ($(".listen-carousel.slick-initialized").length) {
      $(".listen-carousel").slick("slickPause");
    }
  })
  .on("beforeChange", ".listen-carousel", function() {
    $(this).find(".dope-result.expanded").removeClass("expanded");
    $(".listen-collapse.show").collapse("hide");
  })
  .on("beforeChange", ".popular-carousel", function (e, slick, currentSlide, nextSlide) {
    // halfway point
    var carousel = $(this);
    var half = carousel.find(".slick-slide").length - 1;
    if (currentSlide < half) {
      // cut-off point after 16 genres
      var cut = 16;
      if (currentSlide < cut && nextSlide >= cut ||
          currentSlide >= cut && nextSlide < cut) {
        toggleButtons($(".popular-button"));
        $(".popular .results-bar span").toggleClass("d-none");
      }
    } else {
      // cut-off point + halfway point
      cut = cut + half;
      if (currentSlide < cut && nextSlide >= cut ||
        currentSlide >= cut && nextSlide < cut) {
        toggleButtons($(".popular-button"));
        $(".popular .results-bar span").toggleClass("d-none");
      }
    }
  })
  .on("show.bs.collapse", ".options-collapse", function(e) {
    e.stopPropagation();
    $(".options-collapse.show").collapse("hide");
  })
  .on("shown.bs.collapse hidden.bs.collapse", ".collapse", function (e) {
    $(".is_stuck").trigger("sticky_kit:recalc");
  })  
  .on("show.bs.collapse", ".settings-collapse", function(e) {
    e.stopPropagation();
    $(".settings-collapse.show").collapse("hide");
    removeErrors();
  })
  // if all settings-collapses are hidden, show first one
  .on("hidden.bs.collapse", ".settings-collapse", function(e) {
    if (!$(".settings .dope-options .btn-dope[aria-expanded=true]").length) {
      $(".settings-collapse:first").collapse("show");
    }
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
  .on("click", ".expandable .exp", function() {
    var button = $(this);
    button.parents(".results").find(".expandable.expanded").removeClass("expanded");
    if (button.attr("aria-expanded") === "true") {
      button.parents(".expandable").addClass("expanded");
    }
  })
  // removes focus from buttons when clicked
  .on("click", ".btn-dope, .dope-link, .dope-dot, .episode-header, .search-button", function() {
    $(this).blur();
  })
  // empties search field when link or button is clicked
  .on("click", "a, button:not(.search-button)", function() {
    $(".q").val("");
  })
  // hides dopebar-collapse...
  .on("click", "body, .dope-link, .search-button", function() {
    $("#dopebar-collapse.show").collapse("hide");
  })
  // ...except when dopebar-collapose is clicked
  .on("click", "#dopebar-collapse", function(e) {
    e.stopPropagation();
  })
  .on("click", "#scroll-up", function() {
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
    var buttons = $(".selectable");
    if (buttons.length) {
      if (button.hasClass("active")) {
        buttons.removeClass("selected");
      }
      else {
        buttons.addClass("selected");
      }
      button.toggleClass("active");
    }
  })
  .on("click", ".errors .btn-dope", function() {
    removeErrors();
  });

$(window)
  .on("popstate", function(e) {
    var state = e.originalEvent.state;
    if (state) {
      // if url in urls, reload results (and don't push)
      var url = state.url;
      var urls = ["settings"];
      var context = $(state.context);
      for (var i = 0; i < urls.length; i++) {
        if (url.includes(urls[i]) ||
            context.hasClass("splash") ||
            context.hasClass("dashboard")) {
          var drop = $("#center-stage");
          return getResults([url, drop, false], false, true);
        }
      }
      $("#center-stage").html(state.context);
      titleUpdater();
      if (context.hasClass("showpod")) {
        drop = $("#episodes-content");
        url = url.replace("showpod", "episodes");
        getResults([url, drop, false]);
      }
    }
  })
  .on("blur", function() {
    window.clearInterval(charts);
    window.clearInterval(previous);
  })
  .on("focus", function() {
    previousUpdater();
    chartsUpdater();
  })
  .on("resize", function() {
    hoverDisabler();
  });