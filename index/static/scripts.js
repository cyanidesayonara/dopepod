function pushState(url) {
  url = url.replace("episodes", "showpod");
  // return if url in urls
  var urls = ["dopebar", "charts", "last_played", "unsubscribe"];
  for (i = 0; i < urls.length; i++) {
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
};
function replaceState(url) {
  url = url.replace("episodes", "showpod");
  // return if url in urls
  var urls = ["dopebar", "charts", "last_played"];
  for (i = 0; i < urls.length; i++) {
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
  loadResults(["/dopebar/", "#dopebar"]);
  loadResults(["/last_played/", "#last-played"])
};
// abort previous ajax request if url not in urls
function checkForXHR(url) {
  if(xhr != null) {
    var urls = ["dopebar", "charts", "episodes", "last_played"];
    for (i = 0; i < urls.length; i++) {
      if (url.includes(urls[i])) {
        return;
      }
    }
    xhr.abort();
    xhr = null;
  }
};
// LOADER
function loadResults(args, no_push) {
  var url = args[0];
  // sometimes object, sometimes just a string
  var drop = $(args[1]);
  var callback = args[2];
  var args = args[3];
  checkForXHR(url);
  // don't push when loading results via popstate
  if (!no_push) {
    pushState(url);
  }
  if (!drop.find(".loading").length && url != "/dopebar/" && url != "/last_played/") {
    if (drop.children(".results").length) {
      drop.children(".results").replaceWith(getLoading());
    }
  }
  xhr = $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
  })
    .done(function(response) {
      drop.html(response);
      // loads episodes (cuz drop dun exist yet)
      if (callback) {
        callback(args);
        // if page refresh, apply theme
        if (drop.is("#dopebar")) {
          changeTheme(!drop.find(".lights-toggle").hasClass("lit"));
        }
      }
      replaceState(url);
    });
};
// SCROLLERS
function scrollSpy() {
  $(window).scroll(function() {
    scrollUp();
    footer();
  });
}
function footer() {
  var x = $("#footer").offset().top;
  var y = $(window).scrollTop() + $(window).height();
  if (x > y) {
    $("#player").addClass("fixed-bottom");
  }
  else {
    $("#player").removeClass("fixed-bottom");
  }
}
function scrollUp() {
  var scroll = $(window).scrollTop();
  if (scroll > 300) {
    $(".scroll-up").removeClass("d-none");
  }
  else {
    $(".scroll-up").addClass("d-none");
  }
}
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
};
function changeTheme(theme) {
  if (theme) {
    $("body").addClass("darken");
  }
  else {
    $("body").removeClass("darken");
  }
};
function postSubscriptions(podids, button) {
  clearTimeout(timeout);
  timeout = setTimeout(function() {
    button.html(getButtonLoading());
    $.ajax({
      method: "POST",
      url: "/subscriptions/",
      data: {
        "podids": podids,
      },
    })
    .fail(function(xhr, ajaxOptions, thrownError) {
      $("#center-stage").html(xhr.responseText);
      replaceState("/");
    })
    .done(function(response) {
      console.log(button)
      if (button.hasClass("sub-button")) {
        var url = "/showpod/" + podids[0] + "/";
        var drop = "#center-stage";
        var args = ["/episodes/" + podids[0] + "/", ".showpod .results-content"];
        loadResults([url, drop, loadResults, args]);
      }
      else {
        $("#center-stage").html(response);
      }
    });
  }, 250);
};
function postPlaylist(data, mode, button) {
  var drop = $("#center-stage");
  var text = button[0].innerHTML;
  button.html(getButtonLoading());
  $.ajax({
    method: "POST",
    url: "/playlist/",
    data: data,
  })
  // nothing to continue
  .fail(function (xhr, ajaxOptions, thrownError) {
    button.html(text);
    $("#player").empty();
  })
  .done(function (response) {
    if (mode == "play") {
      $("#player").html(response);
      updateTitle();
      button.html(text);
      // gotta wait a sec here
      setTimeout(function () {
        var box = $("#player-wrapper h1");
        var text = $("#player-wrapper h1 span");
        scrollText(box, text);
      }, 1000);
      if (drop.find(".playlist").length) {
        loadResults([url, drop]);
      }
    }
    else {
      if (mode == "add") {
        button.text(text);
      }
      if (drop.find(".playlist").length) {
        loadResults([url, drop]);
      }
    }
  });
};
function playNext() {
  var data = {
    "pos": "0",
    "mode": "play",
  };
  var mode = "play";
  var wrapper = $("#player-wrapper");
  wrapper.find("audio")[0].preload = "none";
  wrapper.empty();
  // wait a sec here
  timeout = setTimeout(function () {
    postPlaylist(data, mode, wrapper);
  }, 500);
};
// replaces spaces/&s with +, removes unwanted chars
function cleanString(q) {
  q = q.replace(/&+/g, "+");
  q = q.replace(/\s+/g, "+");
  q = q.replace(/([^a-zA-Z0-9\u0080-\uFFFF +']+)/gi, "");
  return q.toLowerCase();
};
function cookieBannerClose() {
  $("#player").empty();
};
function getButtonLoading() {
  return $(".button-loading").first().clone();
};
function getLoading() {
  return $(".loading").first().clone();
};
function updateLastPlayed() {
  last_played = setInterval(function () {
    loadResults(["/last_played/", "#last-played"]);
  }, 1000 * 60);
};
function updateCharts() {
  charts = setInterval(function () {
    loadResults(["/charts/", "#charts"]);
  }, 1000 * 60 * 60 * 24);
};

$(document)
  .ready(function() {
    xhr = null;
    timeout = 0;
    last_played = 0;
    charts = 0;
    refreshCookie();
    scrollUp();
    footer();
    scrollToTop();
    scrollSpy();
    updateLastPlayed();
    updateCharts();
  })
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
        q = cleanString(q);
        var drop = $("#center-stage");
        url = url + "?q=" + q;
        if (!(drop.find(".results-header").data("q") == q)) {
          loadResults([url, drop]);
        }
        scrollToTop();
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
      loadResults([url, drop]);
      scrollTo(drop);
    }, 250);
  })
  // search when user clicks buttons
  .on("click", ".showpod-buttons .options-button", function(e) {
    e.preventDefault();
    // redirect to episodes
    var url = this.href.replace("showpod", "episodes");
    var button = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function () {
      button.html(getButtonLoading());
      var drop = button.parents(".results-content");
      loadResults([url, drop]);
      scrollTo(drop);
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
      var args = ["/episodes/" + podid + "/", ".showpod .results-content"];
      loadResults([url, drop, loadResults, args]);
    }
    else {
      drop.find(".results-collapse").collapse("show");
    }
    scrollToTop();
  })  
  // LOGIN & SIGNUP
  // show splash / dashboard / login / register / password reset
  .on("click", ".login-link, .signup-link, .password-link, .index-link, .results-close", function(e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    var link = $(this);
    if (!drop.find(".login").length && !drop.find(".dashboard").length) {
      loadResults([url, drop]);
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
    } 
    scrollToTop();
  })
  .on("click", ".browse-link", function(e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    if (!drop.find(".list").length) {
      loadResults([url, drop]);
    }
    else {
      drop.find(".results-collapse").collapse("show");
    }
    scrollToTop();
  })
  .on("click", ".subscriptions-link", function(e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    if (!drop.find(".subscriptions").length) {
      loadResults([url, drop]);
    }
    else {
      drop.find(".results-collapse").collapse("show");
    }
    scrollToTop();
  })
  .on("click", ".settings-link", function(e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    if (!drop.find(".settings").length) {
      loadResults([url, drop]);
    }
    else {
      drop.find(".results-collapse").collapse("show");
    }
    scrollToTop();
  })
  .on("click", ".playlist-link", function(e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    if (!drop.find(".playlist").length) {
      loadResults([url, drop]);
    }
    else {
      drop.find(".results-collapse").collapse("show");
    }
    scrollToTop();
  })
  .on("click", ".charts-link", function(e) {
    e.preventDefault();
    scrollTo($("#charts"));
  })
  .on("click", ".last-played-link", function(e) {
    e.preventDefault();
    scrollTo($("#last-played"));
  })
  .on("click", ".update-playlist", function(e) {
    e.preventDefault();
    var url = this.href;
    clearTimeout(timeout);
    timeout = setTimeout(function () {
      var drop = $("#center-stage");
      loadResults([url, drop]);
    }, 250);
  })
  .on("click", ".update-last-played", function(e) {
    e.preventDefault();
    var url = this.href;
    clearTimeout(timeout);
    timeout = setTimeout(function () {
      var drop = $("#last-played");
      loadResults([url, drop]);
    }, 250);
  })
  // sub or unsub
  .on("submit", ".subscriptions-form", function(e) {
    e.preventDefault();
    var podids = [];
    var form = $(this);
    podids[0] = form.find("input[name^=podids]").val();
    var button = form.find("button[type=submit]");
    postSubscriptions(podids, button);
  })
  // unsubscribe one or more podcasts
  // POST ajax request, data is array of podids
  .on("click", ".unsubscribe-button", function(e) {
    e.preventDefault();
    var button = $(this);
    var podids = [];
    // array of all selected podids
    var buttons = button.parent().parent().siblings().find(".subscriptions-result.selected");
    if (buttons.length) {
      buttons.each(function (i, button) {
        podids[i] = $(button).data("podid");
      })
    }
    // if nothing selected, do nothing
    else {
      return;
    }
    postSubscriptions(podids, button);
  })
  // playlist - play, add, move, or delete episode
  .on("submit", ".playlist-form", function(e) {
    e.preventDefault();
    var form = $(this);
    if (!form.find(".button-loading").length) {
      clearTimeout(timeout);
      timeout = setTimeout(function () {
        var data = form.serialize();
        var mode = form.find("input[name=mode]").val();
        var button = form.find("button[type=submit]");
        postPlaylist(data, mode, button);
      }, 250);
    }
  })
  // close player
  .on("click", ".player-close", function(e) {
    e.preventDefault();
    $(this).parents().siblings("audio")[0].preload="none";
    $("#player").empty();
    updateTitle();
  })
  // minimize player
  .on("click", ".player-minimize", function(e) {
    e.preventDefault();
    $("#player-collapse").collapse("hide");
    $("#player-close-collapse").collapse("hide");
    $(this).toggleClass("active")
    .parents("#player-wrapper").toggleClass("minimize")
  })
  // save settings, apply theme
  .on("submit", ".settings-form", function(e) {
    e.preventDefault();
    var method = this.method;
    var url = this.action;
    var form = $(this)
    var data = form.serialize();
    var theme = form.find("input[name=dark_theme]").is(":checked");
    form.find("button[type=submit]").html(getButtonLoading());
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
        pushState(url);
        if (theme) {
          $(".lights-toggle").removeClass("lit");
        } else {
          $(".lights-toggle").addClass("lit");
        }
        changeTheme(theme);
        $("#center-stage").html(response);
        scrollToTop();
        replaceState("/");
      });
  })
  // login or signup and refresh page/send password link
  .on("submit", ".login-form, .signup-form, .password-form", function(e) {
    e.preventDefault();
    var method = this.method;
    var url = this.action;
    var form = $(this);
    var data = form.serialize();
    var button = form.find("button[type=submit]");
    var text = button[0].innerText;
    button.html(getButtonLoading());
    $.ajax({
      data: data,
      method: method,
      url: url,
    })
      // returns errors
      .fail(function(xhr, ajaxOptions, thrownError) {
        button.text(text);
        $("#center-stage").html(xhr.responseText);
        scrollToTop();
      })
      // returns splashboard
      .done(function(response) {
        $("#center-stage").html(response);
        // if not password reset, refresh page
        if (text != "Send") {
          refreshCookie();
          refreshPage();
        }
        scrollToTop();
        });
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
  .on("mouseenter mouseleave", ".view-button, .provider-button", function() {
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
      scrollTo(obj);
    }, 250);
  })
  .on("show.bs.collapse", ".last-played-collapse", function(e) {
    e.stopPropagation();
    $(".last-played-collapse.show").collapse("hide");
    var obj = $(this).parents();
    timeout = setTimeout(function () {
      scrollTo(obj);
    }, 250);
  })
  .on("show.bs.collapse", ".options-collapse", function(e) {
    e.stopPropagation();
    $(".options-collapse.show").collapse("hide");
  })
  .on("click", ".episodes-button, .reviews-button", function(e) {
    e.stopPropagation();
    $(".showpod-collapse").collapse("toggle");
  })
  // toggles background theme
  .on("click", ".lights-toggle", function(e) {
    e.preventDefault();
    $(".lights-toggle").toggleClass("lit");
    changeTheme(!$(".lights-toggle").hasClass("lit"));
  })
  // removes focus from buttons when clicked
  .on("click", ".btn-dope, .dopebar-link, .last-played-toggle, .episode-header", function() {
    $(this).blur();
  })
  // empties search field when link or button is clicked
  .on("click", "a, button", function() {
    $(".q").val("");
  })
  // deletes error text (after delay) when clicking anywhere
  .on("click", "body", function() {
    $(".errors").delay(2000).fadeOut();
  })
  // hides dopebar-collapse...
  .on("click", "body, .dopebar-link, .search-button", function() {
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
    var box = $(this).parents(".subscriptions-result").toggleClass("selected");
    var buttons = box.parents(".results").find(".subscriptions-result");
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
      button.parent().parent().siblings().find(".subscriptions-result").removeClass("selected");
    }
    else {
      button.parent().parent().siblings().find(".subscriptions-result").addClass("selected");
    }
    button.toggleClass("active");
  });

$(window)
  .on("popstate", function(e) {
    var state = e.originalEvent.state;
    if (state) {
      // if url in urls, reload results (and don't push)
      var url = state.url;
      var urls = ["settings", "playlist", "subscriptions"];
      for (i = 0; i < urls.length; i++) {
        if (url.includes(urls[i])) {
          var drop = $("#center-stage");
          loadResults([url, drop], true);
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