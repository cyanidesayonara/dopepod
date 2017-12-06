$(window).on("popstate", function(event) {
  var state = event.originalEvent.state;
  if (state) {
    $("#results").html(state.context);
    $("title")[0].innerText = state.title;

    // if (state.q) {
    //   $("#q").val(state.q);
    // }
    // if (state.alphabet) {
    //   $("input[name='alphabet'][value=' + state.alphabet + ']").prop("checked", true);
    // }
    // if (state.view) {
    //   $("input[name='view'][value=' + state.view + ']").prop("checked", true);
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
  var context = $("#results")[0].innerHTML;
  var url = $("#results")[0].baseURI;
  var title = "dopepod";
  var state = {
    "context": context,
    "title": title,
  };

  if ($("#podinfo").length) {
    title = $("#podinfo h3")[0].innerHTML;
  }

  history.pushState(state, "", url);
  $("title")[0].innerText = title;
}

function replaceState(url) {
  var context = $("#results")[0].innerHTML;
  var title = "dopepod";
  var state = {
    "context": context,
    "title": title,
  };

  if (!url || url == "/charts/") {
    var url = "/";
  }

  if ($("#podinfo").length) {
    title = $("#podinfo h3")[0].innerHTML;
  }

  history.replaceState(state, "", url);
  $("title")[0].innerText = title;
}

function loadEpisodes(itunesid) {
  // load episodes for podcast
  // TODO also load on back button
  $('#results').html("<div class='col' id='overlay'></div>");
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
      $("#results").html(response);
      $('#overlay').hide();
      var url = $("#main-content")[0].baseURI;
      replaceState(url);
    });
}

function openStage() {
  $("#stage").addClass("open");
  $("#bar").addClass("extended");
  $("#main").toggle();
}

function loadResults(url) {
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

function loadStage(url) {
  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      if (response.html) {
        $("#stage").html(response.html);
      }
      else {
        $("#stage").html(response);
      }
      replaceState(url);
    });
}

function scrollToTop() {
  $('html, body').animate({
    scrollTop: $("#main-content").offset().top
  }, 200);
}

function scrollToBar() {
  $('html, body').animate({
    scrollTop: $("#multi-bar-scroll").offset().top
  }, 200);
}

function refreshPage() {
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
      $("#nav-content").html(response);
      // go to index
      loadResults("/charts/");
      showSearch();
    });
}

// ye ajax search function
function SearchFunc(url, page) {
  /* if there is a previous ajax request, then we abort it and then set xhr to null */
  if(xhr != null) {
    xhr.abort();
    xhr = null;
  }

  data = {}
  if ($("#search-bar").css("display") != "none") {
    var q = $("#q").val();
    if (q) {
      data["q"] = q;
    }
  }
  else if ($("#browse-bar").css("display") != "none") {
    var alphabet = $("input[name=alphabet]:checked").val();
    if (alphabet) {
      data["alphabet"] = $("input[name=alphabet]:checked").val();
    }
  }
  if ($("#options-bar").length) {
    if ($("#genre-buttons").length) {
      var genre = $("input[name=genre]:checked").val();
      if (genre != "All") {
        data["genre"] = genre;
      }
    }
    if ($("#language-buttons").length) {
      var language = $("input[name=language]:checked").val();
      if (language != "All") {
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

  copyurl = url;

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
        var url = copyurl + "?" + $.param(data);
      }
      replaceState(url);
    });
}

function showSearch() {
  if ($("#search-bar").css("display") == "none") {
    toggleBars();
  }
}

function showBrowse() {
  if ($("#browse-bar").css("display") == "none") {
    toggleBars();
  }
}

function toggleBars() {
  $("#search-bar").toggle();
  $("#browse-bar").toggle();
}

// after page loads
$(document)
  .ready(function() {
    // refresh cookie
    refreshCookie();
    // initialize bootstrap tooltips
    $("[data-toggle='tooltip']").tooltip();
    xhr = null;
    timeout = 0;
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
      pushState();
      SearchFunc(url, false);
    }, 250);
    scrollToBar()
  })
  // search when "search" button is clicked
  .on("submit", "#search-form, #browse-form", function(e) {
    e.preventDefault();
    var url = this.action;
    pushState();
    SearchFunc(url, false);
    scrollToBar()
  })
  .on("change", "#alphabet-buttons", function() {
    var url = $("#browse-form")[0].action;
    pushState();
    SearchFunc(url, false);
    scrollToBar()
  })
  .on("submit", "#result-form", function(e) {
    e.preventDefault();
    var url = this.action;
    var form = $(this).serialize();
    console.log(form);
    pushState();
    SearchFunc(url, true);
  })
  // search when user changes options
  .on("change", "#page-buttons, #genre-buttons, #language-buttons, #view-buttons", function() {
    var url = $("#result-form")[0].action;
    pushState();
    SearchFunc(url, true);
  })
  // show podinfo
  .on("click", ".show-podinfo", function(e) {
    e.preventDefault();
    var url = this.href;
    var itunesid = $(this).data("itunesid");
    pushState();
    showSearch();
    loadStage(url);
    scrollToTop();
    loadEpisodes(itunesid);

  })
  // go to home view
  .on("click", ".index-link", function(e) {
    e.preventDefault();
    pushState();
    showSearch();
    loadResults("/charts/");
  })
  // open browse
  .on("click", ".browse-link", function(e) {
    e.preventDefault();
    pushState();
    showBrowse();
    loadResults("/browse/");
   })
  .on("click", ".search-toggle", function(e) {
    e.preventDefault();
    pushState();
    toggleBars();
    replaceState();
  })
  // open subscriptions
  .on("click", ".subscriptions-link", function(e) {
    e.preventDefault();
    pushState();
    showSearch();
    loadResults("/subscriptions/");
  })
  // open settings
  .on("click", ".settings-link", function(e) {
    e.preventDefault();
    pushState();
    showSearch();
    loadStage("/settings/");
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
        $("#stage").html(xhr.responseJSON.html);
      })
      .done(function(response) {
        showSearch();
        loadResults("/charts/");
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
    // Stop form from submitting normally
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
        loadStage("/account/login/");
      })
      .done(function(response) {
        button.html(response);

        var url = $("#main-content")[0].baseURI;
        var context = $("#main-content")[0].innerHTML;
        if ($("#podinfo").length) {
          var title = $("#podinfo h3")[0].innerHTML;
        }

        var state = {
          "context": context,
          "title": title,
        };
        history.replaceState(state, "", url);
      });
  })
  // open login register or password reset in modal
  .on("click", ".ajax-login, .ajax-register, .login-link, .signup-link, .password-link", function(e) {
    e.preventDefault();
    var url = this.href;
    loadStage(url);
  })
  // login or signup, refresh after
  .on("submit", ".login-form, .signup-form", function (e) {
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
        $("#stage").html(xhr.responseJSON.html);
      })
      .done(function() {
        $("#stage").html("");
        refreshCookie();
        refreshPage();
        loadResults("/charts/");
      });
  })
