// HISTORY API
$(window).on("popstate", function(event) {
  var state = event.originalEvent.state;
  if (state) {
    $("#main-wrapper").html(state.context);
    $("title")[0].innerText = state.title;

    // if (state.q) {
    //   $("#q").val(state.q);
    // }
    // if (state.alphabet) {
    //   $("input[name='alphabet'][value=' + state.alphabet + ']").prop("checked", true);
    // }
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
  var context = $("#main-wrapper")[0].innerHTML;
  var title = "dopepod";
  var state = {
    "context": context,
    "title": title,
  };

  if (!url || url == "/charts/") {
    var url = "/";
  }

  history.replaceState(state, "", url);
  updateTitle();
}
function updateTitle() {
  var title = "dopepod";
  var el = $("#player-content");
  if (el.length) {
    title += " | now playing: " + el.find("#player-title")[0].innerText + " - " + el.find("#player-episode")[0].innerText;
  }
  else if ($("#podinfo").length) {
      title += " - " + $("#podinfo-title")[0].innerText;
  }


  $("title")[0].innerText = title;
}

// LOGIN REFRESH
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
  // refresh navbar (and maybe other stuff as well?)
  $.ajax({
    type: "GET",
    url: "/navbar/",
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
      // console.log(thrownError);
    })
    .done(function(response) {
      // refresh page
      $("#episodes").empty();
      $("#results").empty();
      loadChart();
      $("#navbar-drop").html(response);
    });
}

function clearSearch() {
  $("#q").val("");
  $("#alphabet-buttons").find(".alphabet-button.active").removeClass("active");
}

// LOADERS
function loadCenterStage(url) {
  $("#center-stage").html("<div class='col-auto results-loading'><i class='fas fa-circle-notch fa-spin icon loading-icon'></i><span>Loading...</span></div>");
  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      // console.log(thrownError);
    })
    .done(function(response) {
      $("#center-stage").html(response);
      replaceState(url);
    });
}
function loadEpisodes(itunesid) {
  $("#episodes").html("<div class='col-auto results-loading'><i class='fas fa-circle-notch fa-spin icon loading-icon'></i><span>Loading episodes...</span></div>");
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
function loadResults(url) {
  $("#episodes").empty();
  $("#results").html("<div class='col-auto results-loading'><i class='fas fa-circle-notch fa-spin icon loading-icon'></i><span>Loading results...</span></div>");
  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      // console.log(thrownError);
    })
    .done(function(response) {
      $("#results").html(response);
      replaceState(url);
    });
}
function loadChart() {
  $("#chart").html("<div class='col-auto results-loading'><i class='fas fa-circle-notch fa-spin icon loading-icon'></i><span>Loading charts...</span></div>");
  var url = "/charts/";
  var genre = $("input[name=chart-genre]:checked").val();
  if (!genre) {
    genre = $("input[name=chart-selected-genre]:checked").val();
  }
  if (genre && genre != 'All') {
    data = {
      "genre": genre
    };
    url = url + "?" + $.param(data);
  }

  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      // console.log(thrownError);
    })
    .done(function(response) {
      $("#charts").html(response);
    });
}
// ye ajax search function
function SearchFunc(url, q=null, page=null) {
  if(xhr != null) {
    xhr.abort();
    xhr = null;
  }

  data = {};

  if (q) {
    data["q"] = q;
  }
  else {
    url ="/browse/";
  }

  var genre = $("input[name=genre]:checked").val();
  if (!genre) {
    genre = $("input[name=selected-genre]:checked").val();
  }
  if (genre && genre != 'All') {
    data["genre"] = genre;
  }

  var language = $("input[name=language]:checked").val();
  if (!language) {
    language = $("input[name=selected-language]:checked").val();
  }
  if (language && language != 'All') {
    data["language"] = language;
  }

  if (page) {
    var page = $("input[name=page]:checked").val();
    if (page && page != '1') {
      data["page"] = page;
    }
  }

  scrollToMultibar();
  $("#episodes").empty();
  $("#results").html("<div class='col-auto results-loading'><span class='results-info'>Loading results...</span></div>");

  xhr = $.ajax({
    method: "GET",
    url: url,
    data: data,
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
      // console.log(thrownError);
    })
    .done(function(response) {
      $("#results").html(response);
      if (!jQuery.isEmptyObject(data)) {
        url = url + "?" + $.param(data);
      }
      replaceState(url);
    });
}

// SCROLLTO
function scrollToTop() {
  $("#browse-collapse").collapse("hide");
  $('html, body').animate({
    scrollTop: $("body").offset().top
  }, 350);
}
function scrollToMultibar() {
  $("#browse-collapse").collapse("hide");
  $('html, body').animate({
    scrollTop: 400
  }, 350);
}

// after page loads
$(document)
  .ready(function() {
    // refresh cookie
    refreshCookie();
    xhr = null;
    timeout = 0;
  })
  // SEARCH
  // search when user types into search field (with min "delay" between keypresses)
  .on("keyup", "#search-form", function() {
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = $("#search-form")[0].action;
      var q = $("#q").val();
      pushState();
      SearchFunc(url, q);
    }, 250);
  })
  // search when "search" button is clicked
  .on("submit", "#search-form", function(e) {
    e.preventDefault();
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = $("#search-form")[0].action;
      var q = $("#q").val();
      pushState();
      SearchFunc(url, q);
      clearSearch();
    }, 250);
  })
  // BROWSE
  // browse when "browse" button is clicked
  .on("submit", "#browse-form", function(e) {
    e.preventDefault();
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = $("#browse-form")[0].action;
      var q = $("input[name=alphabet]:checked").val();
      pushState();
      SearchFunc(url, q);
      clearSearch();
    }, 250);
  })
  .on("change", "#alphabet-buttons", function() {
    var url = $("#browse-form")[0].action;
    var q = $("input[name=alphabet]:checked").val();
    pushState();
    SearchFunc(url, q);
    clearSearch();
  })
  //RESULTS
  .on("submit", "#results-form", function(e) {
    e.preventDefault();
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = $("#results-form")[0].action;
      var q = $("input[name=selected-q]:checked").val();
      pushState();
      SearchFunc(url, q);
      clearSearch();
    }, 250);
  })
  // search when user changes options
  .on("change", "#page-buttons", function() {
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = $("#results-form")[0].action;
      var q = $("input[name=selected-q]:checked").val();
      pushState();
      SearchFunc(url, q, true);
      clearSearch();
    }, 250);
  })
  // search when user changes options
  .on("change", "#genre-buttons, #language-buttons, #selected-buttons", function() {
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = $("#results-form")[0].action;
      var q = $("input[name=selected-q]:checked").val();
      pushState();
      SearchFunc(url, q);
      clearSearch();
    }, 250);
  })
  // CHARTS
  .on("submit", "#chart-form", function(e) {
    e.preventDefault();
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      loadChart();
    }, 250);
  })
  .on("change", "#chart-genre-buttons, #chart-selected-buttons", function() {
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      loadChart();
    }, 250);
  })
  // NAVIGATION
  // show podinfo
  .on("click", ".show-podinfo", function(e) {
    e.preventDefault();
    var url = this.href;
    var itunesid = $(this).data("itunesid");
    pushState();
    clearSearch();
    loadCenterStage(url);
    loadEpisodes(itunesid);
    scrollToTop();
  })
  // go to home view
  .on("click", ".index-link", function(e) {
    e.preventDefault();
    pushState();
    var url = this.href;
    pushState();
    clearSearch();
    loadCenterStage(url);
    $("#episodes").empty();
    scrollToTop();
  })
  // open browse
  .on("click", ".browse-link", function(e) {
    e.preventDefault();
    var url = this.href;
    pushState();
    clearSearch();
    loadResults(url);
    scrollToMultibar();
   })
  // open subscriptions
  .on("click", ".subscriptions-link", function(e) {
    e.preventDefault();
    var url = this.href;
    pushState();
    clearSearch();
    loadResults(url);
    scrollToMultibar();
  })
  // open settings
  .on("click", ".settings-link", function(e) {
    e.preventDefault();
    var url = this.href;
    pushState();
    clearSearch();
    loadCenterStage(url);
    $("#episodes").empty();
    scrollToTop();
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
        button.text("Oops :p");
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
    $("#pills-password-tab").tab("show");
  })
  .on("click", ".login-toggle", function() {
    $("#login-errors").empty();
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
        $("#login-errors").html("<div class='error-message'>" + xhr.responseText + "</div>");
        button.text("Log In");
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
        $("#login-errors").html("<div class='error-message'>" + xhr.responseText + "</div>");
        button.text("Reset");
      })
      .done(function() {
        loadCenterStage("/")
        scrollToTop();
      });
  })
  .on("click", "#show-episodes", function(e) {
    e.preventDefault();
    var el = $("#episode-collapse");
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
  // BOOTSTRAP COLLAPSES
  .on("show.bs.collapse", ".more-collapse", function (e) {
      $(".more-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".options-collapse", function (e) {
      $(".options-collapse.show").collapse("hide");
  })
  .on("show.bs.collapse", ".chart-options-collapse", function (e) {
      $(".chart-options-collapse.show").collapse("hide");
  })
