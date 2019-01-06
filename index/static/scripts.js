"use strict";

let xhr = null;
let timeout = 0;
let previous = 0;
let charts = 0;

refreshCookie();
dateLocalizer();
hoverDisabler();
// consent is given by default when entering site
// user may choose to deny it later
_paq.push(["rememberConsentGiven"]);

// post user's local time zone to server
// give new datestring to date-elements
function dateLocalizer() {
  // post user's local time zone to server
  let tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  $.ajax({
    data: {
      "tz": tz,
    },
    method: "POST",
    url: "/tz/",
  });

  // give new datestring to date-elements
  let date = new Date();
  // local time offset in seconds
  let offset = -date.getTimezoneOffset() * 60;
  let dates = document.querySelectorAll(".date");
  Array.prototype.forEach.call(dates, function (date, i) {
    // get utc as milliseconds
    let utc = date.getAttribute("data-utc");
    // add offset
    let d = +utc + +offset;
    // multiply to seconds and create date object
    d = new Date(d * 1000)
    // format datestring
    let dateString =
      ("0" + d.getUTCDate()).slice(-2) + " " +
      ((d.toLocaleString("en-us", {
        month: "short"
      }))) + " " +
      d.getUTCFullYear() + " " +
      ("0" + d.getUTCHours()).slice(-2) + ":" +
      ("0" + d.getUTCMinutes()).slice(-2);
    date.innerText = dateString;
  });
};
function giveConsent() {
  _paq.push(["rememberConsentGiven"]);
};
function denyConsent() {
  _paq.push(["forgetConsentGiven"]);
};
// send page view data to be analyzed
function trackView(url) {
  _paq.push(['requireConsent']);
  _paq.push(["trackPageView", url]);
};
// send search data to be analyzed
function trackSearch(q) {
  _paq.push(['requireConsent']);
  _paq.push(["trackSiteSearch", q]);
};
// push current state & url into browser history
function pushState(url) {
  // return if url in urls
  const urls = ["episodes", "dopebar", "subscriptions", "playlist", "charts", "previous", "change-password"];
  for (let i = 0; i < urls.length; i++) {
    if (url.includes(urls[i])) {
      return;
    }
  }
  titleUpdater();
  const context = document.getElementById("center-stage").innerHTML;
  const state = {
    "context": context,
    "url": url,
  };
  history.pushState(state, "", url);
  trackView(url);
};
// replace current state & url in browser history
function replaceState(url) {
  url = url.replace("episodes", "showpod");
  // return if url in urls
  const urls = ["dopebar", "subscriptions", "playlist", "charts", "previous", "change-password"];
  for (let i = 0; i < urls.length; i++) {
    if (url.includes(urls[i])) {
      return;
    }
  }
  // ignore these urls, use current url instead
  if (!url || url.includes("unsubscribe")) {
    url = document.baseURI;
  }
  titleUpdater();
  const context = document.getElementById("center-stage").innerHTML;
  const state = {
    "context": context,
    "url": url,
  };
  history.replaceState(state, "", url);
};
// updates page title
function titleUpdater() {
  // default title
  let title = "dopepod";
  // get title from player or center-stage
  const pw = document.getElementById("player-wrapper");
  if (pw) {
    title = pw.getAttribute("data-title")
  } else {
    const cs = document.getElementById("center-stage").querySelector(".results");
    if (cs) {
      title = cs.getAttribute("data-title");
    }
  }
  document.title = title;
};
// extracts csrftoken (or other data) from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = jQuery.trim(cookies[i]);
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
  const csrftoken = getCookie("csrftoken");
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });
};
// refreshes page on login
function refreshPage() {
  getResults(["/dopebar/", "dopebar-wrapper", false], true);
  getResults(["/previous/", "previous", false], true);
  getResults(["/charts/", "charts", false], true);
  getResults(["/subscriptions/", "subscriptions", false], true);
  getResults(["/playlist/", "playlist", false], true);
};
// abort previous ajax request if url not in urls
function checkForXHR(url) {
  if (xhr != null) {
    const urls = ["dopebar", "charts", "episodes", "previous", "subscriptions", "playlist"];
    for (let i = 0; i < urls.length; i++) {
      if (url.includes(urls[i])) {
        return;
      }
    }
    xhr.abort();
    xhr = null;
  }
};

function enableLoader(el, url) {
  if (el.id == "player") {
    // blur player
    addClass(el.querySelector("#player-content"), "blurred");
  } else if (el.id == "episodes-content") {
    // blur all children except loader
    let blurrables = children(el, ":not(.loader)");
    if (blurrables) {
      Array.prototype.forEach.call(blurrables, function (blurrable, i) {
        addClass(blurrable, "blurred");
      });
    }
  } else {
    let blurrables = children(el, ":not(.loader)");
    if (blurrables) {
      Array.prototype.forEach.call(blurrables, function (blurrable, i) {
        addClass(blurrable, "blurred");
      });
    }
  }
  const loaders = el.querySelectorAll(".loader");
  let loader = loaders[loaders.length - 1];
  // show loader
  addClass(loader, "d-block");
  // set url for reload button
  if (url) {
    loader.querySelector(".reload-button").setAttribute("href", url);
  }
};
// RESULTS
function getResults(args, noLoader, noPush) {
  const url = args[0];
  let drop = args[1];
  // drop is sometimes element, sometimes just an id string (when callbacking)
  if (typeof drop === "string" || drop instanceof String) {
    drop = document.getElementById(drop);
  }
  const scroll = args[2];
  const callback = args[3];
  const callbackArgs = args[4];
  checkForXHR(url);
  if (!noPush) {
    pushState(url);
  }
  if (!noLoader) {
    const rc = drop.querySelector(".results-collapse");
    if (rc && !hasClass(rc, "show")) {
      $(rc).collapse("show");
    }
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
    .fail(function (xhr, ajaxOptions, thrownError) {
      // if episodes fail, call noshow
      if (url.includes("/episodes/") && thrownError != "abort") {
        podid = url.split("/")[2];
        if (podid) {
          noshow(podid);
        }
      } else if (url.includes("previous")) {
        window.clearInterval(previous);
      } else if (url.includes("charts")) {
        window.clearInterval(charts);
      }
    })
    .done(function (response) {
      drop.innerHTML = response;
      lazyload();
      // loads episodes
      if (callback) {
        callback(callbackArgs);
      }
      // if page refresh, apply theme
      else if (drop.id == "dopebar-wrapper") {
        let response = drop.querySelector("#dopebar");
        const theme = response.getAttribute("data-theme");
        response.removeAttribute("data-theme");
        themeChanger(theme);
      } else if (children(drop, ".splash").length) {
        initPlay();
      } else if (drop.id == "subscriptions" || drop.id == "playlist") {
        $(drop).trigger("sticky_kit:recalc");
      }
      if (scroll) {
        if ((url.includes("/charts/") || url.includes("/previous/")) && $(window).width() < 992) {
          scrollTo(drop);
        }
      }
      replaceState(url);
    });
};
// jquery function replacements
function addClass(el, className) {
  if (el.classList) {
    el.classList.add(className);
  } else {
    el.className += " " + className;
  }
};

function removeClass(el, className) {
  if (el.classList) {
    el.classList.remove(className);
  } else {
    el.className = el.className.replace(new RegExp("(^|\\b)" + className.split(" ").join("|") + "(\\b|$)", "gi"), " ");
  }
};

function toggleClass(el, className) {
  if (el.classList) {
    el.classList.toggle(className);
  } else {
    const classes = el.className.split(" ");
    const existingIndex = classes.indexOf(className);

    if (existingIndex >= 0) {
      classes.splice(existingIndex, 1);
    } else {
      classes.push(className);
    }
    el.className = classes.join(" ");
  }
};

function hasClass(el, className) {
  if (el.classList) {
    return el.classList.contains(className);
  } else {
    return new RegExp("(^| )" + className + "( |$)", "gi").test(el.className);
  }
};

function parents(node, className) {
  let current = node;
  while (current.parentElement != null) {
    current = current.parentElement;
    if (current.classList.contains(className)) {
      return current;
    }
  }
};

function children(node, name) {
  let array = [];
  const nodes = node.childNodes;
  if (nodes) {
    Array.prototype.forEach.call(nodes, function (node, i) {
      if (selectorMatches(node, name)) {
        array.push(node);
      }
    });
  }
  return array;
};

function selectorMatches(element, selector) {
  if (typeof element.matches == "function" && element.matches(selector))
    return element;
  if (typeof element.matchesSelector == "function" && element.matchesSelector(selector))
    return element;
  const matches = (element.document || element.ownerDocument).querySelectorAll(selector);
  if (matches) {
    Array.prototype.forEach.call(matches, function (match, i) {
      if (match == element) {
        return match;
      }
    })
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
// SCROLLIES
function scrollSpy() {
  scrollUp();
  playerUnfixer();
  columnFixer();
};

function scrollUp() {
  let scroll = $(window).scrollTop();
  let button = document.getElementById("scroll-up");
  if (scroll > 300) {
    addClass(button, "d-inline-block");
  } else {
    removeClass(button, "d-inline-block");
  }
};

function scrollToTop() {
  $("html, body").animate({
    scrollTop: $("body").offset().top
  }, 250);
};

function scrollTo(obj) {
  $("html, body").animate({
    scrollTop: $(obj).offset().top - 44
  }, 250);
};
// scrolls header text in player if text is wider than box
function scrollText(box, text) {
  const boxWidth = box.innerWidth();
  const textWidth = text.width();
  if (textWidth > boxWidth) {
    const animSpeed = textWidth * 30;
    $(box)
      .animate({
        scrollLeft: (textWidth - boxWidth)
      }, animSpeed)
      .animate({
        scrollLeft: 0
      }, animSpeed, function () {
        setTimeout(function () {
          scrollText(box, text);
        }, 1000);
      })
  }
};

function playerUnfixer() {
  const x = $("#footer").offset().top;
  const y = $(window).scrollTop() + $(window).height();
  if (x > y) {
    addClass(document.getElementById("player"), "fixed-bottom");
  } else {
    removeClass(document.getElementById("player"), "fixed-bottom");
  }
};

function columnFixer() {
  $("#subscriptions, #playlist").stick_in_parent({
    offset_top: 44
  });
};

function themeChanger(theme) {
  const themes = ["light", "dark"];
  for (let i = 0; i < themes.length; i++) {
    if (theme.includes(themes[i])) {
      document.body.className = "";
      addClass(document.body, theme);
    }
  }
};

function postContact(form) {
  const method = form.method;
  const url = form.action;
  const data = $(form).serialize();
  const drop = document.getElementById("center-stage");
  $.ajax({
      data: data,
      method: method,
      url: url,
    })
    .fail(function (xhr, ajaxOptions, thrownError) {
      drop.innerHTML = xhr.responseText;
      scrollToTop();
    })
    .done(function (response) {
      $(drop).html(response);
      scrollToTop();
      replaceState(url);
    });
  enableLoader(drop, url);
};

function postSettings(form) {
  const button = form.querySelector("button[type=submit]");
  const theme = button.getAttribute("data-theme");
  button.parentNode.querySelector("input[name=theme]").value = theme;
  const method = form.method;
  const url = form.action;
  const data = $(form).serialize();
  const drop = document.getElementById("center-stage");
  $.ajax({
      data: data,
      method: method,
      url: url,
    })
    .fail(function (xhr, ajaxOptions, thrownError) {
      drop.innerHTML = xhr.responseText;
      scrollToTop();
    })
    .done(function (response) {
      if (theme) {
        themeChanger(theme);
      }
      $(drop).html(response);
      scrollToTop();
      replaceState(url);
    });
  enableLoader(drop, url);
};

function postLogin(form) {
  const method = form.method;
  const url = form.action;
  const data = $(form).serialize();
  const drop = document.getElementById("center-stage");
  const button = form.querySelector("button[type=submit].btn-dope");
  if (button) {
    button.innerHTML = getButtonLoading();
  }
  $.ajax({
      data: data,
      method: method,
      url: url,
    })
    // returns errors
    .fail(function (xhr, ajaxOptions, thrownError) {
      drop.innerHTML = xhr.responseText;
      scrollToTop();
    })
    // returns splashboard
    .done(function (response) {
      getResults(["/", drop, true], false, true);
      // if not password reset, refresh page
      if (hasClass(form, "login-form") || hasClass(form, "tryout-form")) {
        refreshCookie();
        refreshPage();
      }
    });
};

function postSubscriptions(form, origPodid, origButton) {
  let button = origButton;
  let podid = origPodid;
  if (form) {
    button = form.querySelector("button[type=submit]");
    podid = form.querySelector("input[name^=podid]").value;
  }
  if (podid) {
    const drop = document.getElementById("subscriptions");
    $.ajax({
        method: "POST",
        url: "/subscriptions/",
        data: {
          "podid": podid,
        },
      })
      .fail(function (xhr, ajaxOptions, thrownError) {})
      .done(function (response) {
        drop.innerHTML = response;
        const el = document.querySelector(".results.showpod");
        if (el) {
          const current_podid = el.getAttribute("data-podid");
          if (podid == current_podid) {
            const args = ["/episodes/" + podid + "/", "episodes-content", false];
            getResults(["/showpod/" + podid, "center-stage", false, getResults, args], false, true);
          }
        }
        getResults(["/charts/", "charts", false]);
        $(drop).trigger("sticky_kit:recalc");
      });
    button.innerHTML = getButtonLoading();
  }
};

function postPlaylist(form, origData, origMode, origButton, origPos) {
  let data = origData;
  let mode = origMode;
  let button = origButton;
  let pos = origPos;
  let text = undefined;
  if (form) {
    data = $(form).serialize();
    mode = form.querySelector("input[name=mode]").value;
    button = form.querySelector("button[type=submit]");
    pos = form.querySelector("input[name=pos]");
  }
  if (pos && !origPos) {
    pos = pos.value;
  }
  const drop = document.getElementById("playlist");
  if (button) {
    text = button.innerHTML;
  }
  const url = "/playlist/";
  if (mode == "play") {
    const wrapper = document.getElementById("player-wrapper");
    if (wrapper) {
      removeClass(wrapper, "minimize");
      const audio = document.getElementById("audio");
      audio.preload = "none";
      enableLoader(document.getElementById("player"));
    }
  }
  $.ajax({
      method: "POST",
      url: url,
      data: data,
    })
    // nothing to continue
    .fail(function (xhr, ajaxOptions, thrownError) {
      if (button) {
        button.innerHTML = text;
      }      
      document.getElementById("player").innerHTML = "";
      // TODO if playlist fails
    })
    .done(function (response) {
      if (mode == "play") {
        let player = document.getElementById("player");
        player.innerHTML = response;
        titleUpdater();
        if (button) {
          button.innerHTML = text;
        }
        // gotta wait a sec here
        setTimeout(function () {
          const box = $(player).find("h1");
          const text = $(player).find("h1 span");
          scrollText(box, text);
        }, 1000);
        if (pos && drop.childNodes.length) {
          getResults([url, drop, false]);
        }
      } else {
        if (button && mode == "add") {
          button.innerHTML = text;
        }
        drop.innerHTML = response;
        lazyload();
      }
      $(drop).trigger("sticky_kit:recalc");
    });
  if (button) {
    button.innerHTML = getButtonLoading();
  }
};

function playNext() {
  const mode = "play";
  const pos = "1";
  const data = {
    "mode": mode,
    "pos": pos,
  };
  const button = undefined;
  postPlaylist(undefined, data, mode, button, pos);
};

function closePlayer() {
  document.getElementById("audio").preload = "none";
  document.getElementById("player").innerHTML = '';
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
  return document.getElementById("button-loading").outerHTML;
};

function previousUpdater() {
  previous = setInterval(function () {
    const drop = document.getElementById("previous");
    if (!drop.querySelectorAll(".expandable.expanded").length) {
      getResults(["/previous/", "previous", false], true);
    }
  }, 1000 * 60);
};

function chartsUpdater() {
  charts = setInterval(function () {
    const drop = document.getElementById("charts");
    if (!drop.querySelectorAll(".expandable.expanded").length) {
      getResults(["/charts/", "charts", false], true);
    }
  }, 1000 * 60 * 60 * 24);
};

function hasTouch() {
  return navigator.maxTouchPoints || navigator.msMaxTouchPoints;
};

function hoverDisabler() {
  if (hasTouch()) {
    removeClass(document.documentElement, "no-touch");
  } else {
    addClass(document.documentElement, "no-touch");
  }
};

function initPopular() {
  $("#popular-carousel")
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

function initPlay() {
  const elements = document.querySelectorAll(".logo");
  Array.prototype.forEach.call(elements, function (el, i) {
    toggleClass(el, "d-none")
  })
  // shuffle all except first (logo)
  const carousel = document.getElementById("play-carousel");
  if (carousel) {
    let slides = Array.from(carousel.childNodes);
    const first = slides.shift();
    for (let i = slides.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const temp = slides[i];
      slides[i] = slides[j];
      slides[j] = temp;
    }
    slides.unshift(first);
    $("#play-carousel")
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
  }
};

function removeErrors() {
  const el = document.getElementById("errors");
  if (el) {
    el.parentNode.removeChild(el);
  }
};

function lazyload() {
  const myLazyLoad = new LazyLoad({
    elements_selector: ".lazyload"
  });
};

function toggleButtons(elements) {
  // change icons on both buttons
  Array.prototype.forEach.call(elements, function (el, i) {
    let icons = Array.from(el.childNodes);
    // lose first node (title)
    icons.shift();
    // toggle classes on remaining two (icons)
    Array.prototype.forEach.call(icons, function (icon, i) {
      toggleClass(icon, "d-none");
    });
  });
};

function togglePopular() {
  const carousel = $("#popular-carousel");
  const index = carousel.slick("slickCurrentSlide");
  const cut = 16;
  if (index >= cut) {
    carousel.slick("slickGoTo", 0);
  } else if (index < cut) {
    carousel.slick("slickGoTo", cut);
  }
};

$(document)
  .ready(function () {
    lazyload();
    replaceState(window.location.href);
    scrollSpy();
    initPlay();
    initPopular();
    previousUpdater();
    chartsUpdater();
  })
  .scroll(function () {
    scrollSpy();
  })
  // SEARCH
  // search when user types into search field (with min "delay" between keypresses)
  .on("submit", ".search-form", function (e) {
    e.preventDefault();
    const form = this;
    let url = form.action;
    let q = form.querySelector(".q").value;
    if (q) {
      q = cleanString(q);
      const drop = document.getElementById("center-stage");
      if (!(drop.querySelector(".results").getAttribute("data-q") == q)) {
        url = url + "?q=" + q;
        getResults([url, drop, true]);
        trackSearch(q);
      } else {
        scrollTo(drop);
      }
    }
  })
  // sub or unsub
  .on("submit", ".subscriptions-form", function (e) {
    e.preventDefault();
    const form = this;
    clearTimeout(timeout);
    timeout = setTimeout(function () {
      postSubscriptions(form);
    }, 250);
  })
  // unsubscribe one or more podcasts
  // POST ajax request, data is array of podids
  .on("click", ".unsubscribe-button", function (e) {
    e.preventDefault();
    const button = this;
    const selecteds = parents(button, "results").querySelectorAll(".selectable.selected");
    const podids = [];
    if (selecteds.length) {
      if (hasClass(button, "exp")) {
        return;
      }
      // array of all selected podid
      Array.prototype.forEach.call(selecteds, function (selected, i) {
        podids[i] = selected.getAttribute("data-podid");
      });
    }
    // if nothing selected, do nothing
    else {
      return;
    }
    if (podids.length) {
      postSubscriptions(undefined, podids, button);
    }
  })
  // playlist - play, add, move, or delete episode
  .on("submit", ".playlist-form", function (e) {
    e.preventDefault();
    const form = this;
    if (!form.querySelector(".button-loading")) {
      clearTimeout(timeout);
      timeout = setTimeout(function () {
        postPlaylist(form);
      }, 250);
    }
  })
  .on("submit", ".contact-form", function (e) {
    e.preventDefault();
    const form = this;
    clearTimeout(timeout);
    timeout = setTimeout(function () {
      postContact(form);
    }, 250);
  })
  // save settings, apply theme
  .on("submit", ".settings-form", function (e) {
    e.preventDefault();
    const form = this;
    clearTimeout(timeout);
    timeout = setTimeout(function () {
      postSettings(form);
    }, 250);
  })
  // login or signup and refresh page/send password link
  .on("submit", ".tryout-form, .login-form, .signup-form, .password-form, .password-reset-form", function (e) {
    e.preventDefault();
    const form = this;
    clearTimeout(timeout);
    timeout = setTimeout(function () {
      postLogin(form);
    }, 250);
  })
  .on("submit", ".convert-form", function (e) {
    e.preventDefault();
    alert("This feature doesn't work yet. Sorry!");
  })
  .on("click", ".subscriptions-link", function (e) {
    e.preventDefault();
    scrollTo(document.getElementById("subscriptions"));
  })
  .on("click", ".playlist-link", function (e) {
    e.preventDefault();
    scrollTo(document.getElementById("playlist"));
  })
  .on("click", ".charts-link", function (e) {
    e.preventDefault();
    scrollTo(document.getElementById("charts"));
  })
  .on("click", ".previous-link", function (e) {
    e.preventDefault();
    scrollTo(document.getElementById("previous"));
  })
  .on("click", ".reload-button", function (e) {
    e.preventDefault();
    const button = this;
    const url = this.href;
    clearTimeout(timeout);
    timeout = setTimeout(function () {
      const drop = parents(button, "results").parentNode;
      if (drop.id == "episodes-content") {
        url = url.replace("showpod", "episodes");
        getResults([url, drop, false]);
      } else {
        const results = drop.querySelector(".results.showpod");
        if (results) {
          const podid = results.getAttribute("data-podid");
          if (podid) {
            const args = ["/episodes/" + podid + "/", "episodes-content", false];
            getResults([url, drop, false, getResults, args]);
          } else {
            getResults([url, drop, false]);
          }
        }
      }
    }, 250);
  })
  .on("click", ".options-button", function (e) {
    e.preventDefault();
    const button = this;
    // redirect to episodes
    clearTimeout(timeout);
    timeout = setTimeout(function () {
      const url = button.href.replace("showpod", "episodes");
      const drop = parents(button, "drop");
      if (hasClass(parents(button, "results"), "showpod")) {
        getResults([url, "episodes-content", false]);
      } else {
        getResults([url, drop, false]);
      }
    }, 250);
  })
  // NAVIGATION
  .on("click", ".showpod-link", function (e) {
    e.preventDefault();
    const button = this;
    timeout = setTimeout(function () {
      const url = button.href;
      const podid = button.getAttribute("data-podid");
      const drop = document.getElementById("center-stage");
      if (!(drop.querySelector(".results").getAttribute("data-podid") == podid)) {
        const args = ["/episodes/" + podid + "/", "episodes-content", false];
        getResults([url, drop, true, getResults, args]);
      } else {
        scrollTo(drop);
      }
    }, 250);
  })
  // LOGIN & SIGNUP
  // show splash / dashboard / login / register / password reset
  .on("click", ".login-link, .signup-link, .password-link, .index-link", function (e) {
    e.preventDefault();
    const button = this;
    clearTimeout(timeout);
    timeout = setTimeout(function () {
      const url = button.href;
      const drop = document.getElementById("center-stage");
      $(drop).find(".results-collapse").collapse("show");
      if (!children(drop, ".splash").length) {
        getResults([url, drop, true]);
      } else {
        if (hasClass(button, "index-link") || hasClass(button, "collapsed")) {
          $(drop).find("#splash-collapse").collapse("show");
        } else if (hasClass(button, "login-link")) {
          $(drop).find("#login-collapse").collapse("show");
        } else if (hasClass(button, "signup-link")) {
          $(drop).find("#signup-collapse").collapse("show");
        } else if (hasClass(button, "password-link")) {
          $(drop).find("#password-collapse").collapse("show");
        }
        scrollTo(drop);
      }
    }, 250);
  })
  .on("click", ".browse-link", function (e) {
    e.preventDefault();
    const button = this;
    clearTimeout(timeout);
    timeout = setTimeout(function () {
      const url = button.href;
      const drop = document.getElementById("center-stage");
      $(drop).find(".results-collapse").collapse("show");
      if (!drop.querySelector(".list, .grid")) {
        getResults([url, drop, true]);
      } else {
        if (window.location.href.includes("?")) {
          getResults([url, drop, true]);
        } else {
          scrollTo(drop);
        }
      }
    }, 250);
  })
  .on("click", ".settings-link", function (e) {
    e.preventDefault();
    const button = this;
    clearTimeout(timeout);
    timeout = setTimeout(function () {
      const url = button.href;
      const drop = document.getElementById("center-stage");
      $(drop).find(".results-collapse").collapse("show");
      if (!children(drop, ".settings").length) {
        getResults([url, drop, true]);
      } else {
        scrollTo(drop);
      }
    }, 250);
  })
  .on("click", ".privacy-link", function (e) {
    e.preventDefault();
    const button = this;
    clearTimeout(timeout);
    timeout = setTimeout(function () {
      const url = button.href;
      const drop = document.getElementById("center-stage");
      $(drop).find(".results-collapse").collapse("show");
      if (!children(drop, ".privacy").length) {
        getResults([url, drop, true]);
      } else {
        scrollTo(drop);
      }
    }, 250);
  })
  .on("click", ".terms-link", function (e) {
    e.preventDefault();
    const button = this;
    timeout = setTimeout(function () {
      const url = button.href;
      const drop = document.getElementById("center-stage");
      $(drop.querySelector(".results-collapse")).collapse("show");
      if (!children(drop, ".terms").length) {
        getResults([url, drop, true]);
      } else {
        scrollTo(drop);
      }
    }, 250);
  })
  .on("click", ".api-link", function (e) {
    e.preventDefault();
    const button = this;
    timeout = setTimeout(function () {
      const url = button.href;
      const drop = document.getElementById("center-stage");
      $(drop).find(".results-collapse").collapse("show");
      if (!children(drop, ".api").length) {
        getResults([url, drop, true]);
      } else {
        scrollTo(drop);
      }
    }, 250);
  })
  .on("click", ".contact-link", function (e) {
    e.preventDefault();
    const button = this;
    timeout = setTimeout(function () {
      const url = button.href;
      const drop = document.getElementById("center-stage");
      $(drop).find(".results-collapse").collapse("show");
      if (!children(drop, ".contact").length) {
        getResults([url, drop, true]);
      } else {
        scrollTo(drop);
      }
    }, 250);
  })
  // minimize player
  .on("click", ".player-minimize", function (e) {
    e.preventDefault();
    let button = this;
    $("#player-collapse").collapse("hide");
    $("#confirm-collapse-player").collapse("hide");
    if (button.getAttribute("aria-expanded") == "true") {
      button.setAttribute("aria-expanded", "false");
    } else {
      button.setAttribute("aria-expanded", "true");
    }
    toggleClass(document.getElementById("player-wrapper"), "minimize");
  })
  .on("click", ".theme-button[type=submit]", function () {
    const button = this;
    const theme = button.querySelector("span").innerText.toLowerCase();
    button.parentNode.querySelector("input[name=theme]").value = theme;
  })
  .on("click", ".showpod-button", function (e) {
    const button = this;
    e.preventDefault();
    // if button not pressed
    if (button.querySelector(".d-none.active")) {
      Array.prototype.forEach.call(document.querySelectorAll(".showpod-content"), function (el, i) {
        toggleClass(el, "d-none");
      });
      toggleButtons(document.querySelectorAll(".showpod-button"));
    }
    scrollTo(document.querySelector(".showpod-content:not(.d-none)"));
  })
  .on("click", ".popular-button", function (e) {
    e.preventDefault();
    // if button not pressed
    if (this.querySelector(".d-none.active")) {
      togglePopular();
    }
  })
  // toggle view icon & view collapse on click
  .on("click", ".view-button", function (e) {
    e.preventDefault();
    const button = this;
    const view = button.querySelector(".d-none").getAttribute("data-view");
    let results = parents(button, "results");
    results.setAttribute("data-view", view);
    toggleButtons(button);
    $(results).find(".view-collapse").collapse("toggle");
  })
  .on("click", ".select-theme", function (e) {
    e.preventDefault();
    let theme = document.body.getAttribute("class");
    if (theme == "light") {
      theme = "dark";
    } else if (theme == "dark") {
      theme = "light";
    }
    themeChanger(theme);
  })
  .on("click", ".expandable .exp", function (e) {
    e.preventDefault();
    const button = this;
    const expanded = parents(button, "results").querySelector(".expandable.expanded");
    if (expanded) {
      removeClass(expanded, "expanded");
    }
    if (button.getAttribute("aria-expanded") === "true") {
      addClass(parents(button, "expandable"), "expanded");
    }
  })
  // removes focus from buttons when clicked
  .on("click", ".btn-dope, .dope-link, .dope-dot, .episode-header, .search-button", function () {
    this.blur();
  })
  // empties search field when link or button is clicked
  .on("click", "a, button:not(.search-button)", function () {
    let qs = document.querySelectorAll(".q");
    Array.prototype.forEach.call(qs, function (q, i) {
      q.value = "";
    })
  })
  // hides dopebar-collapse...
  .on("click", "body, .dope-link, .search-button", function () {
    $("#dopebar-collapse.show").collapse("hide");
  })
  // ...except when dopebar-collapose is clicked
  .on("click", "#dopebar-collapse", function (e) {
    e.stopPropagation();
  })
  .on("click", "#scroll-up", function () {
    scrollToTop();
  })
  .on("click", ".select", function () {
    toggleClass(parents(this, "selectable"), "selected");
    const container = parents(this, "results");
    const selectables = container.querySelectorAll(".selectable");
    const selected = container.querySelectorAll(".selectable.selected");
    if (selectables.length == selected.length) {
      addClass(container.querySelector(".select-all"), "active");
    } else {
      removeClass(container.querySelector(".select-all"), "active");
    }
  })
  // selects all subscriptions (and maybe all playlist episodes as well TODO?)
  .on("click", ".select-all", function () {
    const button = this;
    const container = parents(this, "results");
    const selectables = container.querySelectorAll(".selectable");
    if (selectables.length) {
      if (hasClass(button, "active")) {
        Array.prototype.forEach.call(selectables, function (selectable, i) {
          removeClass(selectable, "selected");
        })
      } else {
        Array.prototype.forEach.call(selectables, function (selectable, i) {
          addClass(selectable, "selected");
        })
      }
      toggleClass(button, "active");
    }
  })
  .on("click", "#errors .btn-dope", function () {
    removeErrors();
  })
  // BOOTSTRAP COLLAPSES
  .on("show.bs.collapse", ".login-collapse", function (e) {
    e.stopPropagation();
    $(children(this.parentNode, ".login-collapse.show")).collapse("hide");
    removeErrors();
  })
  .on("show.bs.collapse", ".more-collapse", function (e) {
    e.stopPropagation();
    $(parents(this, "results")).find(".more-collapse.show").collapse("hide");
  })
  // for cols that use sticky kit
  .on("shown.bs.collapse hidden.bs.collapse", "#subscriptions .collapse, #playlist .collapse", function (e) {
    e.stopPropagation();
    const drop = parents(this, "drop");
    // wait for height to settle
    setTimeout(function () {
      $(drop).trigger("sticky_kit:recalc");
    }, 500);
  })
  .on("show.bs.collapse", "#play-carousel .more-collapse", function (e) {
    e.stopPropagation();
    $("#play-carousel").slick("slickPause");
  })
  .on("hide.bs.collapse", "#play-carousel .more-collapse", function (e) {
    e.stopPropagation();
    $("#play-carousel").slick("slickPlay");
  })
  .on("show.bs.collapse", "#splash-collapse", function () {
    const carousel = document.getElementById("play-carousel");
    if (hasClass(carousel, "slick-initialized")) {
      $(carousel).slick("slickPlay");
      $(carousel).slick("slickGoTo", 0);
    }
  })
  .on("hide.bs.collapse", "#splash-collapse", function () {
    $(this).find(".more-collapse.show").collapse("hide");
    const carousel = document.getElementById("play-carousel");
    if (hasClass(carousel, "slick-initialized")) {
      $(carousel).slick("slickPause");
    }
  })
  .on("beforeChange", "#play-carousel", function () {
    $(this).find(".expandable.expanded").removeClass("expanded");
    $(this).find(".more-collapse.show").collapse("hide");
  })
  .on("beforeChange", "#popular-carousel", function (e, slick, currentSlide, nextSlide) {
    // halfway point
    const carousel = this;
    const half = carousel.querySelectorAll(".slick-slide").length - 1;
    if (currentSlide < half) {
      // cut-off point after 16 genres
      const cut = 16;
      if (currentSlide < cut && nextSlide >= cut ||
        currentSlide >= cut && nextSlide < cut) {
        toggleButtons(document.querySelectorAll(".popular-button"));
        const labels = document.querySelectorAll(".popular .results-bar span");
        Array.prototype.forEach.call(labels, function (label, i) {
          toggleClass(label, "d-none");
        })
      }
    } else {
      // cut-off point + halfway point
      cut = cut + half;
      if (currentSlide < cut && nextSlide >= cut ||
        currentSlide >= cut && nextSlide < cut) {
        toggleButtons(document.querySelectorAll(".popular-button"));
        const labels = document.querySelectorAll("popular .results-bar span");
        Array.prototype.forEach.call(labels, function (icon, i) {
          toggleClass(label, "d-none");
        })
      }
    }
  })
  .on("show.bs.collapse", ".options-collapse", function (e) {
    e.stopPropagation();
    $(".options-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".settings-collapse", function (e) {
    e.stopPropagation();
    $(".settings-collapse.show").collapse("hide");
    removeErrors();
  })
  // if all settings-collapses are hidden, show first one
  .on("hidden.bs.collapse", ".settings-collapse", function (e) {
    if (!document.querySelector(".settings .dope-options .btn-dope[aria-expanded=true]")) {
      $(".settings-collapse:first").collapse("show");
    }
  });

$(window)
  .on("popstate", function (e) {
    const state = e.originalEvent.state;
    if (state) {
      // if url in urls, reload results (and don't push)
      let url = state.url;
      const urls = ["settings"];
      const drop = document.getElementById("center-stage");
      for (let i = 0; i < urls.length; i++) {
        if (url.includes(urls[i])) {
          return getResults([url, drop, false], false, true);
        }
      }
      drop.innerHTML = state.context;
      if (hasClass(drop.querySelector(".results"), "splash")) {
        return getResults([url, drop, false], false, true);
      } 
      if (hasClass(drop.querySelector(".results"), "showpod")) {
        url = url.replace("showpod", "episodes");
        return getResults([url, "episodes-content", false]);
      }
      lazyload();
      titleUpdater();
    }
  })
  .on("blur", function () {
    window.clearInterval(charts);
    window.clearInterval(previous);
  })
  .on("focus", function () {
    previousUpdater();
    chartsUpdater();
  })
  .on("resize", function () {
    hoverDisabler();
  });