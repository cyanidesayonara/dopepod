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

function pushState() {
  var el = $("#main-wrapper")[0];
  var context = el.innerHTML;
  var url = el.baseURI;
  var title = "dopepod";
  var state = {
    "context": context,
    "title": title,
  };

  if ($("#podinfo").length) {
    title = $("#podinfo-title")[0].innerText;
  }

  history.pushState(state, "", url);
  $("title")[0].innerText = title;
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

  if ($("#podinfo").length) {
    title = $("#podinfo-title")[0].innerText;
  }

  history.replaceState(state, "", url);
  $("title")[0].innerText = title;
}

function loadEpisodes(itunesid) {
  // load episodes for podcast
  // TODO also load on back button
  $("#episodes").html("Loading episodes...");
  $.ajax({
    method: "POST",
    url: "/episodes/",
    data: {
      "itunesid": itunesid,
    },
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      if ($("#podinfo-main").length) {
        $("#episodes").html(response);
        var url = $("#main-wrapper")[0].baseURI;
        replaceState(url);
      }
    });
}

function loadResults(url) {
  $("#results").html("Loading results...");
  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      $("#results").html(response);
      replaceState(url);
    });
}

function loadSplash(url, signup) {
  $("#splash").html("<div class='row' style='height:400px;'><div>");
  if (!signup) {
    signup = null;
  }
  $.ajax({
    type: "POST",
    url: url,
    data: {
      'signup': signup,
    },
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      $("#splash").html(response);
      replaceState("/");
    });
}

function loadCenterStage(url) {
  $("#center-stage").html("<div class='row' style='height:400px;'><div>");
  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      $("#center-stage").html(response);
      replaceState(url);
    });
}

function loadChart() {
  var genre = $("input[name=chart-genre]:checked").val();
  $("#charts").html("Loading charts...");
  var url = "/charts/";
  if (genre != "All") {
    data = {
      "genre": genre,
    };
    url = url + "?" + $.param(data);
  }
  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      $("#charts").html(response);
    });
}

function scrollToTop() {
  $('html, body').animate({
    scrollTop: $("#main-wrapper").offset().top
  }, 200);
}

function scrollToMultibar() {
  $('html, body').animate({
    scrollTop: 400
  }, 200);
}

function refreshNavbar() {
  // refresh navbar (and maybe other stuff as well?)
  $.ajax({
    type: "GET",
    url: "/navbar/",
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
      console.log(thrownError);
    })
    .done(function(response) {
      // refresh navbar
      $("#navbar-drop").html(response);
    });
}

// ye ajax search function
function SearchFunc(url, q, page) {
  /* if there is a previous ajax request, then we abort it and then set xhr to null */
  if(xhr != null) {
    xhr.abort();
    xhr = null;
  }
  $("#results").html("Loading results...");

  data = {
    "q": q,
  }

  if ($("#results-form").length) {
    if ($("#genre-buttons").length) {
      var genre = $("input[name=genre]:checked").val();
      if (genre && genre != 'All') {
        data["genre"] = genre;
      }
    }
    if ($("#language-buttons").length) {
      var language = $("input[name=language]:checked").val();
      if (language && language != 'All') {
        data["language"] = language;
      }
    }
    if (page) {
      if ($("#page-buttons").length) {
        var page = $("input[name=page]:checked").val();
        data["page"] = page;
      }
    }
  }

  xhr = $.ajax({
    method: "GET",
    url: url,
    data: data,
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
      console.log(thrownError);
    })
    .done(function(response) {
      $("#results").html(response);
      if (!jQuery.isEmptyObject(data)) {
        url = url + "?" + $.param(data);
      }
      scrollToMultibar();
      replaceState(url);
    });
  return xhr;
}

function showStage() {
  $("#stage").addClass("open");
  $("#flap").addClass("extended");
}

function hideStage() {
  $("#stage").removeClass("open");
  $("#flap").removeClass("extended");
}

// after page loads
$(document)
  .ready(function() {
    // refresh cookie
    refreshCookie();
    xhr = null;
    timeout = 0;
  })
  .on("show.bs.collapse", function () {
    $(".more-collapse.show").collapse("hide");
  })
  // remove focus from button (focus would be saved on state)
  .on("click", "#search-button, #alphabet-buttons, #genre-buttons, #language-buttons, #view-buttons", function() {
    $(this.children).removeClass("focus");
  })
  // search when user types into search field (with min "delay" between keypresses)
  .on("keyup", "#search-form", function() {
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = $("#search-form")[0].action;
      var q = $("#q").val();
      if (q) {
        pushState();
        SearchFunc(url, q, false);
      }
    }, 250);
  })
  // search when "search" button is clicked
  .on("submit", "#search-form", function(e) {
    e.preventDefault();
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = $("#search-form")[0].action;
      var q = $("#q").val();
      if (q) {
        pushState();
        SearchFunc(url, q, false);
      }
    }, 250);
  })
  // browse when "browse" button is clicked
  .on("submit", "#browse-form", function(e) {
      e.preventDefault();
      clearTimeout(timeout);
      timeout = setTimeout(function() {
        var url = $("#browse-form")[0].action;
        var q = $("input[name=alphabet]:checked").val();
        if (q) {
          pushState();
          SearchFunc(url, q, false);

        }
      }, 250);
    })
  .on("change", "#alphabet-buttons", function() {
    var url = $("#browse-form")[0].action;
    var q = $("input[name=alphabet]:checked").val();
    pushState();
    SearchFunc(url, q, false);
    scrollToMultibar();
 })
  .on("submit", "#results-form", function(e) {
    e.preventDefault();
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = $("#results-form")[0].action;
      if ($("#selected_alphabet").length) {
        var q = $("#selected_alphabet").val();
      }
      else {
        var q = $("#selected_q").val();
      }
      if (q) {
        pushState();
        SearchFunc(url, q, false);
      }
    }, 250);
  })
  // search when user changes options
  .on("change", "#page-buttons", function() {
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = $("#results-form")[0].action;
      if ($("#selected_alphabet").length) {
        var q = $("#selected_alphabet").val();
      }
      else {
        var q = $("#selected_q").val();
      }
      if (q) {
        pushState();
        SearchFunc(url, q, true);
      }
    }, 250);
  })
  // search when user changes options
  .on("change", "#genre-buttons, #language-buttons", function() {
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      var url = $("#results-form")[0].action;
      if ($("#selected_alphabet").length) {
        var q = $("#selected_alphabet").val();
      }
      else {
        var q = $("#q").val();
      }
      if (q) {
        pushState();
        SearchFunc(url, q, false);
      }
    }, 250);
  })
  .on("submit", "#chart-form", function(e) {
    e.preventDefault();
    loadChart();
  })
  .on("change", "#chart-genre-buttons", function() {
    loadChart();
  })
  // show podinfo
  .on("click", ".show-podinfo", function(e) {
    e.preventDefault();
    var url = this.href;
    var itunesid = $(this).data("itunesid");
    pushState();
    loadCenterStage(url);
    loadEpisodes(itunesid);
    $("#browse-bar").addClass("d-none");
    $("#splash").html("");
    $("#episodes").html("");
    scrollToTop();
  })
  // go to home view
  .on("click", ".index-link", function(e) {
    e.preventDefault();
    pushState();
    loadSplash("/dashboard/");
    $("#browse-bar").addClass("d-none");
    $("#center-stage").html("");
    $("#results").html("");
    $("#episodes").html("");
    scrollToTop();
  })
  // open browse
  .on("click", ".browse-link", function(e) {
    e.preventDefault();
    pushState();
    loadResults("/browse/");
    $("#browse-bar").removeClass("d-none");
    $("#episodes").html("");
    scrollToMultibar();
   })
  // open subscriptions
  .on("click", ".subscriptions-link", function(e) {
    e.preventDefault();
    pushState();
    loadResults("/subscriptions/");
    $("#episodes").html("");
    scrollToMultibar();
    $("#browse-bar").addClass("d-none");
  })
  // open settings
  .on("click", ".settings-link", function(e) {
    e.preventDefault();
    pushState();
    $("#splash").html("");
    loadCenterStage("/settings/");
    $("#browse-bar").addClass("d-none");
    $("episodes").html("");
    scrollToTop();
  })
  .on("click", "#browse-toggle", function(e) {
    e.preventDefault();
    if ($("#browse-bar").hasClass("d-none")) {
      $("#browse-bar").removeClass("d-none");
    }
    else {
      $("#browse-bar").addClass("d-none");
    }

  })
  // replace settings, empty and hide modal
  .on("submit", "#settings-form", function (e) {
    e.preventDefault();
    var data = $(this).serialize();
    var method = this.method;
    var url = this.action;
    $.ajax({
      data: data,
      method: method,
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        console.log(thrownError);
        pushState();
        $("#center-stage").html(xhr.responseJSON.html);
      })
      .done(function(response) {
        pushState();
        $("#settings-alert").removeClass("d-none");
      });
  })
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
        console.log(thrownError);
      })
      .done(function(response) {
        $("#player").html(response);
      });
  })
  // close player
  .on("click", "#player-close", function(e) {
    $("#player").empty();
  })
  .on("submit", "#sub-form", function(e) {
    e.preventDefault();
    // button, gets new value
    var button = $(this).find(".sub-button");
    var data = $(this).serialize();
    var url = this.action;
    var method = this.method;
    $.ajax({
      method: method,
      url: url,
      data: data,
    })
      .fail(function(xhr, ajaxOptions, thrownError){
        console.log(thrownError);
        // probably not logged in
        loadCenterStage("/account/login/");
      })
      .done(function(response) {
        if (button[0].innerText == "Subscribe") {
          button.text("Unsubscribe");
          button.removeClass("active");
        }
        else {
          button.text("Subscribe");
          button.addClass("active");
        }

        $("#n_subscribers").text(response);

        if (response == "1") {
          $("#subscriber").text("subscriber");
        }
        else {
          $("#subscriber").text("subscribers");
        }

        var url = $("#main-wrapper")[0].baseURI;
        replaceState(url);
      });
  })
  .on("click", ".password-link", function(e) {
    e.preventDefault();
  })
  // open login register
  .on("click", ".ajax-login", function(e) {
    e.preventDefault();
    var url = this.href;
    pushState();
    loadSplash("/dashboard/", false);
    $("#center-stage").html("");
    scrollToTop();
  })
  // open login register
  .on("click", ".ajax-register", function(e) {
    e.preventDefault();
    var url = this.href;
    pushState();
    loadSplash("/dashboard/", true);
    $("#center-stage").html("");
    scrollToTop();
  })
  .on("click", ".login-signup-toggle", function() {
    $("#login-errors").html("");
    $("#signup-errors").html("");
  })
  // login or signup, refresh after
  .on("submit", ".login-form", function (e) {
    e.preventDefault();
    var data = $(this).serialize();
    var method = this.method;
    var url = this.action;
    $.ajax({
      data: data,
      method: method,
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        console.log(thrownError);
        $("#login-errors").html(xhr.responseJSON.html);
      })
      .done(function() {
        refreshCookie();
        refreshNavbar();
        loadSplash("/dashboard/")
        scrollToTop();
      });
  })
  .on("submit", ".signup-form", function (e) {
    e.preventDefault();
    var data = $(this).serialize();
    var method = this.method;
    var url = this.action;
    $.ajax({
      data: data,
      method: method,
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        console.log(thrownError);
        $("#signup-errors").html(xhr.responseJSON.html);
      })
      .done(function() {
        refreshCookie();
        refreshNavbar();
        loadSplash("/dashboard/")
        scrollToTop();
      });
  })
