// HISTORY API
$(window)
  .on("popstate", function(event) {
    var state = event.originalEvent.state;
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
      $("title")[0].innerText = state.title;
    }
  });
function pushState(url) {
  // return if url in urls
  var urls = ["dopebar", "charts", "episodes", "last_played", "unsubscribe"];
  for (i = 0; i < urls.length; i++) {
    if (url.includes(urls[i])) {
      return;
    }
  }
  var main = $("#main");
  var context = main[0].innerHTML;
  var title = updateTitle();
  var state = {
    "context": context,
    "title": title,
    "url": url,
  };
  history.pushState(state, "", url);
};
function replaceState(url) {
  // return if url in urls
  var urls = ["dopebar", "charts", "last_played"];
  for (i = 0; i < urls.length; i++) {
    if (url.includes(urls[i])) {
      return;
    }
  }
  var main = $("#main");
  // ignore these urls, use current url instead
  if (!url || url.includes("unsubscribe") || url.includes("episodes")) {
    url = main[0].baseURI;
  }
  var context = main[0].innerHTML;
  var title = updateTitle();
  var state = {
    "context": context,
    "title": title,
    "url": url,
  };
  history.replaceState(state, "", url);
};
function updateLastPlayed() {
  setInterval(function() {
    loadResults(["/last_played/", "#last-played"]);
  }, 60000);
};
function updateCharts() {
  setInterval(function() {
    loadResults(["/charts/", "#charts"]);
  }, 86400000);
};
// updates page title
function updateTitle() {
  // default title
  var title = "dopepod";
  var player = $(".player-wrapper");
  // if episode is playing
  if (player.length) {
    title = player.find(".player-title")[0].innerText;
    var episode = player.find(".player-episode")[0].innerText;
    title = "Now playing: " + title + " - " + episode + " | on dopepod";
  }
  // if showpod
  else if ($("#showpod-c").length) {
      title = "Listen to episodes of " + $("#showpod-c h1")[0].innerText + " on dopepod";
  }
  $("title")[0].innerText = title;
  return title;
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
  var url = "/dopebar/";
  var drop = "#dopebar";
  loadResults([url, drop, loadResults, ["/last_played/", "#last-played"]]);
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
    drop.find(".results").replaceWith(getLoading());
  }
  xhr = $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
  })
    .done(function(response) {
      drop.html(response);
      // loads episodes / page refresh
      if (callback) {
        callback(args);
        // if page refresh, apply theme
        if (url == "/dopebar/") {
          changeTheme(!$(".lights-toggle").hasClass("lit"));
        }
      }
      // episodes loaded, remove loading anim
      else if ($(response).hasClass("episodes-table")) {
        $(".episodes-button").text("Episodes");
      }
      replaceState(url);
    });
};
// SCROLLERS
function scrollToTop() {
  $("html, body").animate({
    scrollTop: $("body").offset().top
  }, 250);
};
function scrollToCharts() {
  $("html, body").animate({
    scrollTop: $("#left").offset().top - 44
  }, 250);
};
function scrollToLastPlayed() {
  $("html, body").animate({
    scrollTop: $("#right").offset().top - 44
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
function subscribeOrUnsubscribe(form) {
  clearTimeout(timeout);
  timeout = setTimeout(function() {
    var url = form.action;
    var method = form.method;
    form = $(form);
    var podid = form.find("input[name=podid]").val();
    form.find("button[type=submit]").html(getButtonLoading());
    $.ajax({
      method: method,
      url: url,
      data: {
        "podid": podid,
      },
    })
    .fail(function(xhr, ajaxOptions, thrownError) {
      $("#center-stage").html(xhr.responseText);
      replaceState("/");
    })
    .done(function(response) {
      $("#center-stage").html(response);
      var url = "/episodes/" + podid + "/";
      var drop = "#episodes-collapse";
      loadResults([url, drop]);
    });
  }, 250);
};
function yeOldePlaylistFunction(url, data, mode, button) {
  var text = button[0].innerHTML;
  button.html(getButtonLoading());
  $.ajax({
      method: "POST",
      url: url,
      data: data,
    })
    // nothing to continue
    .fail(function (xhr, ajaxOptions, thrownError) {
      button.html(text);
      $("#player").empty();
    })
    .done(function (response) {
      if (mode == "play") {
        var player = $("#player");
        player.html(response);
        updateTitle();
        button.html(text);
        // gotta wait a sec here
        setTimeout(function () {
          var box = $(".player-title");
          var text = $(".player-title h1");
          scrollText(box, text);
        }, 1000);
      }
      else if (mode == "add") {
        button.text(text);
      }
      // if playlist is visible, update it
      if ($("#center-stage").find(".playlist").length) {
        var drop = $("#center-stage");
        var url = "/playlist/";
        loadResults([url, drop]);
      }
    });
};
function playNext() {
  var url = "/playlist/";
  var data = {
    "pos": "0",
    "mode": "play",
  };
  var mode = "play";
  var button = $(".playlist-link");
  yeOldePlaylistFunction(url, data, mode, button);
};
// replaces spaces/&s with +, removes unwanted chars
function replaceChars(q) {
  q = q.replace(/&+/g, "+");
  q = q.replace(/\s+/g, "+");
  q = q.replace(/([^a-zA-Z0-9\u0080-\uFFFF +']+)/gi, "");
  return q;
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
$(document)
  .ready(function() {
    xhr = null;
    timeout = 0;
    refreshCookie();
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
  .on("click", ".options-button", function(e) {
    e.preventDefault();
    var url = this.href;
    var button = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var drop = button.parents(".results").parent();
      loadResults([url, drop]);
    }, 250);
  })
  // NAVIGATION
  .on("click", ".showpod-link", function(e) {
    e.preventDefault();
    var url = this.href;
    var button = $(this);
    var podid = button.data("podid");
    var drop = $("#center-stage");
    if (!(drop.find("#showpod-c").data("podid") == podid)) {
      var args = ["/episodes/" + podid + "/", "#episodes-collapse"];
      loadResults([url, drop, loadResults, args]);
    }
    scrollToTop();
  })  
    // LOGIN & SIGNUP
    // show splash / dashboard / login / register / password reset
    .on("click", ".login-link, .signup-link, .password-link, .index-link, .results-close", function (e) {
      e.preventDefault();
      var url = this.href;
      var drop = $("#center-stage");
      var link = $(this);
      if (!drop.find(".login").length && !drop.find(".dashboard").length) {
        loadResults([url, drop]);
      }
      else {
        if (link.hasClass("login-link")) {
          $("#login-collapse").collapse("show");
        }
        else if (link.hasClass("signup-link")) {
          $("#signup-collapse").collapse("show");
        }
        else if (link.hasClass("password-link")) {
          $("#password-collapse").collapse("show");
        }
        else {
          $("#splash-collapse").collapse("show");
        }
      } 
      scrollToTop();
    })
  .on("click", "", function(e) {

  })
  .on("click", ".browse-link", function(e) {
    e.preventDefault();
    var url = this.href;
    var drop = $("#center-stage");
    if (!drop.find(".list").length) {
      loadResults([url, drop]);
    }
    else {
      $(".results-collapse").collapse("show");
    }
    scrollToTop();
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
    var drop = $("#center-stage");
    if (!drop.find(".subscriptions").length) {
      loadResults([url, drop]);
    }
    else {
      $(".results-collapse").collapse("show");
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
      $(".results-collapse").collapse("show");
    }
    scrollToTop();
  })
  // save settings, apply theme
  .on("submit", ".settings-form", function (e) {
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
      .fail(function(xhr, ajaxOptions, thrownError) {
        $("#center-stage").html(xhr.responseText);
        scrollToTop();
      })
      .done(function(response) {
        pushState(url);
        if (theme) {
          $(".lights-toggle").removeClass("lit");
        }
        else {
          $(".lights-toggle").addClass("lit");
        }
        changeTheme(theme);
        $("#center-stage").html(response);
        scrollToTop();
        replaceState("/");
      });
  })
  // sub or unsub
  .on("submit", ".sub-form", function(e) {
    e.preventDefault();
    subscribeOrUnsubscribe(this);
  })
  // playlist - play, add, move, or delete episode
  .on("submit", ".playlist-form", function (e) {
    e.preventDefault();
    var form = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function () {
      var url = form[0].action;
      var data = form.serialize();
      var mode = form.find("input[name=mode]").val();
      var button = form.find("button[type=submit]");
      yeOldePlaylistFunction(url, data, mode, button);
    }, 250);
  })
  // close player
  .on("click", ".player-close", function(e) {
    e.preventDefault();
    $(this).siblings("audio")[0].preload="none";
    $("#player").empty();
    updateTitle();
  })
  // minimize player
  .on("click", ".player-minimize", function(e) {
    e.preventDefault();
    $(this).toggleClass("active").parents(".player-wrapper").toggleClass("minimize");
  })
  // login or signup and refresh page/send password link
  .on("submit", ".login-form, .signup-form, .password-form", function (e) {
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
        $(".splash-errors").html(xhr.responseText);
        // deletes error text when clicking anywhere
        $("html").on("click", "body", function() {
          $(".splash-errors").empty();
        })
        scrollToTop();
      })
      // returns splashboard
      .done(function(response) {
        $("#center-stage").html(response);
        // if password reset, show login
        if (text == "Send") {
          $("#login-tab").tab("show");
        }
        // else logged in, refresh page
        else {
          refreshCookie();
          refreshPage();
        }
        scrollToTop();
        });
  })
  // toggle search results collapse & view icon on click
  .on("click", ".view-button", function(e) {
    e.preventDefault();
    var button = $(this);
    var collapses = button.parents(".results").find($(".view-collapse"));
    collapses.each(function() {
      $(this).collapse("toggle");
    })
    button.children().each(function() {
      // TODO stop this from flickering
      $(this).toggleClass("d-none");
    });
  })
  // toggle button icon on hover
  .on("mouseenter mouseleave", ".view-button, .provider-button", function() {
    $(this).children().each(function() {
      $(this).toggleClass("d-none");
    });
  })
  // BOOTSTRAP COLLAPSES
  .on("show.bs.collapse", ".login-collapse", function (e) {
    e.stopPropagation()
    $(".login-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".more-collapse", function(e) {
    e.stopPropagation()
    $(".more-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".last-played-collapse", function(e) {
    e.stopPropagation()
    $(".last-played-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".options-collapse", function (e) {
    e.stopPropagation()
    $(".options-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".showpod-collapse", function (e) {
    e.stopPropagation()
    $(".showpod-collapse.show").collapse("hide");
  })
  // toggles background theme
  .on("click", ".lights-toggle", function(e) {
    e.preventDefault();
    $(".lights-toggle").toggleClass("lit");
    changeTheme(!$(".lights-toggle").hasClass("lit"));
  })
  // removes focus from buttons when clicked
  .on("click", ".btn-dope, .dopebar-link, .last-played-toggle, .episodes-table tbody tr", function(e) {
    $(this).blur();
  })
  // hides dopebar-collapse...
  .on("click", "body, .dopebar-link, .search-button", function(e) {
    $("#dopebar-collapse.show").collapse("hide");
  })
  // ...except when dopebar-collapose is clicked
  .on("click", "#dopebar", function(e) {
    e.stopPropagation();
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
      button.parent().siblings().find(".subscriptions-result").removeClass("selected");
    }
    else {
      button.parent().siblings().find(".subscriptions-result").addClass("selected");
    }
    button.toggleClass("active");
  })
  // unsubscribe one or more podcasts
  // POST ajax request, data is array of podids
  .on("click", ".unsubscribe-button", function(e) {
    e.preventDefault();
    var url = this.href;
    var button = $(this);
    var podids = [];
    // array of one podid
    if (button.hasClass("sub-nix")) {
      podids[0] = button.parent().parent().data("podid");
    }
    else {
      // aray of all selected podids
      var buttons = button.parent().siblings().find(".subscriptions-result.selected");
      if (buttons.length) {
        buttons.each(function(i, button) {
          podids[i] = $(button).data("podid");
        })
      }
      // if nothing selected, do nothing
      else {
        return;
      }
    }
    button.html(getButtonLoading());
    $.ajax({
      method: "POST",
      url: url,
      data: {
        "podids": podids,
      },
    })
    // returns splash
    .fail(function(xhr, ajaxOptions, thrownError) {
      $("#center-stage").html(xhr.responseText);
      replaceState("/");
    })
    // returns results
    .done(function(response) {
      $("#center-stage").html(response);
    });
  })