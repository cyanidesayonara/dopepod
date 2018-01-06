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
  var el = $("#player-content");
  if (el.length) {
    title = "Now playing: " + el.find("#player-title")[0].innerText + " - " + el.find("#player-episode")[0].innerText + " | dopepod";
  }
  else if ($("#podinfo").length) {
      title = "Listen to episodes of " + $("#podinfo-title")[0].innerText + " on dopepod";
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
    url: "/navbar/",
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
      // console.log(thrownError);
    })
    .done(function(response) {
      $("#episodes").empty();
      $("#results").empty();
      loadResults("/charts/", $("#charts"));
      $("#navbar-drop").html(response);
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


function loadEpisodes(itunesid) {
  $("#episodes").load("/static/loading.html");
  $.ajax({
    method: "POST",
    url: "/episodes/",
    data: {
      "itunesid": itunesid,
    },
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      // console.log(thrownError);
    })
    .done(function(response) {
      if ($("#podinfo").length) {
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
  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      // console.log(thrownError);
    })
    .done(function(response) {
      drop.html(response);
      replaceState(url);
    });
}

// SCROLLTO
function scrollToTop() {
  $('html, body').animate({
    scrollTop: $("body").offset().top
  }, 250);
}
function scrollToMultibar() {
  $('html, body').animate({
    scrollTop: 400
  }, 250);
}

function addIcons() {
  $("#search-button").html("<i class='fa fa-search icon'></i>");
  var login_buttons = $("#login-buttons");
  if (login_buttons.length) {
    login_buttons.find("#login-tab")[0].href = "#tabs-login";
    login_buttons.find("#signup-tab")[0].href = "#tabs-signup";
    $("#google-icon").html("<i class='fab fa-google icon'></i>");
  }
  var view_button = $("#view-button");
  if (view_button.length) {
    var grid = view_button.find("#view-icon-grid").html("<i class='fas fa-th'></i>");
    var list = view_button.find("#view-icon-list").html("<i class='fas fa-bars'></i>");
  }
}

// after page loads
$(document)
  .ready(function() {
    // refresh cookie
    refreshCookie();
    xhr = null;
    timeout = 0;

    addIcons();
  })
  // SEARCH
  // search when user types into search field (with min "delay" between keypresses)
  .on("webkitAnimationEnd oanimationend msAnimationEnd animationend", "#nothing", function(e) {
    // $("#logo-wrapper").html("<span id='dopepod'>dopepod</span>");
  })
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
      scrollToMultibar();
    }, 250);
  })
  // search when user clicks buttons
  .on("click", ".page-buttons a, .genre-buttons a, .language-buttons a, .selected-buttons a, .genre_rank a", function(e) {
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
      scrollToMultibar()
    }, 250);
  })
  // NAVIGATION
  // show podinfo
  .on("click", ".show-podinfo", function(e) {
    e.preventDefault();
    var el = $(this);
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = el[0].href;
      var itunesid = el.data("itunesid");
      var drop = $("#center-stage");
      pushState();
      loadResults(url, drop);
      clearSearch();
      $("#browse-collapse").collapse("hide");
      loadEpisodes(itunesid);
      scrollToTop();
    }, 250);
  })
  // go to home view
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
      $("#episodes").empty();
      $("#search").empty();
      scrollToTop();
    }, 250);
  })
  // open browse
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
      scrollToMultibar();
    }, 250);
  })
  // open subscriptions
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
      scrollToMultibar();
    }, 250);
  })
  // open settings
  .on("click", ".settings-link", function(e) {
    e.preventDefault();
    var url = this.href;
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      pushState();
      $("#browse-collapse").collapse("hide");
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
        // console.log(thrownError);
        pushState();
        $("#center-stage").html(xhr.responseText);
        button.text("Save");
      })
      .done(function(response) {
        button.text("Saved");
        pushState();
        loadCenterStage("/");
        scrollToTop();
      });
  })
  .on("submit", "#sub-form", function(e) {
    e.preventDefault();
    // button, gets new value
    var button = $(this).find(".sub-button");
    button.text("Loading...");
    var data = $(this).serialize();
    var url = this.action;
    var method = this.method;
    $.ajax({
      method: method,
      url: url,
      data: data,
    })
      .fail(function(xhr, ajaxOptions, thrownError){
        // console.log(thrownError);
        loadCenterStage("/");
      })
      .done(function(response) {
        var url = $("#main-wrapper")[0].baseURI;
        loadCenterStage(url);
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
        // console.log(thrownError);
      })
      .done(function(response) {
        $("#player-drop").html(response);
        updateTitle();
      });
  })
  // close player
  .on("click", "#player-close", function(e) {
    $("#audio-el").preload="none";
    $("#player-drop").empty();
    updateTitle();
  })
  .on("click", "#player-minimize", function(e) {
    if ($("#player-image").hasClass("d-none")) {
      $("#audio-el").removeClass("d-none");
      $("#player-image").removeClass("d-none");
    }
    else {
      $("#audio-el").addClass("d-none");
      $("#player-image").addClass("d-none");
    }
  })
  // LOGIN & SIGNUP
  // open login / register
  .on("click", ".ajax-login, .ajax-signup", function(e) {
    e.preventDefault();
    var url = this.href;
    pushState();
    clearSearch();
    loadCenterStage(url);
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
        // console.log(thrownError);
        $("#center-stage").html(xhr.responseText);
      })
      .done(function(response) {
        refreshCookie();
        refreshPage();
        loadCenterStage("/")
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
        // console.log(thrownError);
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
      var itunesid = $("#podinfo").data("itunesid");
      loadEpisodes(itunesid);
    }
    scrollToMultibar();
  })
  .on("click", ".results-close", function(e) {
    e.preventDefault();
    $(this).parents(".results").remove();
  })
  .on("click", "#view-button", function(e) {
    e.preventDefault();
    var collapses = $(".results-collapse");
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
   .on("click", ".results-minimize", function(e) {
     $(this).parents(".results").find(".options-collapse.show").collapse("hide");
   })
  .on("click", ".btn-dope-tab.toggle", function(e) {
    $(this).parents(".results").find(".results-wrapper.collapse").collapse("show");
  })
