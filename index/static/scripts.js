$(window).on("popstate", function(event) {
  var state = event.originalEvent.state;
  if (state) {
    $("#main-content").html(state.context);
    $("title")[0].innerText = state.title;

    if (state.q) {
      $("#q").val(state.q);
    }
    if (state.alphabet) {
      $("input[name='alphabet'][value=' + state.alphabet + ']").prop("checked", true);
    }
    if (state.view) {
      $("input[name='view'][value=' + state.view + ']").prop("checked", true);
    }
  }
});

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

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};

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
};

function goToIndex(mode) {
  var url = "/"
  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      $("#main-content").html(response);
      $(window).scrollTop(0);

      if (mode == "search") {
        loadContent("/charts/");
      }
      if (mode == "browse") {
        toggleBars();
        SearchFunc(false);
      }
      if (mode == "subs") {
        loadContent("/subscriptions/");
      }
      if (mode == "settings") {
        loadContent("/settings/");
      }
      
      
      var context = $("#main-content")[0].innerHTML;
      var title = "dopepod";
      var state = {
        "context": context,
        "title": title,
      };

      history.replaceState(state, "", url);
      $("title")[0].innerText = title;
    });
};

function loadContent(url) {
  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      $("#results").html(response);
      $(window).scrollTop(0);

      var context = $("#main-content")[0].innerHTML;
      var title = "dopepod";
      var state = {
        "context": context,
        "title": title,
      };

      history.replaceState(state, "", url);
      $("title")[0].innerText = title;
    });
};

function goToModal(url) {
  $.ajax({
    type: "GET",
    url: url,
  })
  .fail(function(xhr, ajaxOptions, thrownError){
    console.log(thrownError);
  })
  .done(function(response) {
    if ($("#modal").css("display") == "none") {
      $("#modal").modal("show");
    }
    $("#modal-content").html(response.html);
  });
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
      goToIndex("search");
    });
};

// ye ajax search function
function SearchFunc(page) {
  /* if there is a previous ajax request, then we abort it and then set xhr to null */
  if(xhr != null) {
    xhr.abort();
    xhr = null;
  }
  
  data = {}
  if ($("#search-bar").css("display") != "none") {
    url = $("#search-form")[0].action;
    var q = $("#q").val();
    if (q) {
      data["q"] = q;
    }
  }
  if ($("#browse-bar").css("display") != "none") {
    url = $("#browse-form")[0].action;
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

      var context = $("#main-content")[0].innerHTML;
      var url = copyurl + "?" + $.param(data);
      var title = "dopepod";
      var state = {
        "context": context,
        "title": title,
        "data": data,
      };
      history.replaceState(state, "", url);
    });
};

function toggleBars() {
  $("#search-bar").toggle();
  $("#browse-bar").toggle();
};

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
      SearchFunc(false);
    }, 250);
  })
  // search when "search" button is clicked
  .on("submit", "#search-form, #browse-form", function(e) {
    e.preventDefault(false);
    SearchFunc();
  })
  .on("change", "#alphabet-buttons", function() {
    SearchFunc(false);
  })
  .on("submit", "#result-form", function(e) {
    e.preventDefault();
    var form = $(this).serialize();
    console.log(form);
    SearchFunc(true);
  })
  // search when user changes options
  .on("change", "#page-buttons, #genre-buttons, #language-buttons, #view-buttons", function() {
    SearchFunc(true);
  })
  // show podinfo
  .on("click", ".show-podinfo", function(e) {
    e.preventDefault();
    var url = this.href;
    $.ajax({
      type: "GET",
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        console.log(thrownError);
      })
      .done(function(response) {
        $("#stage").html(response);
        $("#stage").css("height", "100vh");
        $("#stage").css("padding-top", "100px");
        $("#bar").css("top", "-100vh");

        var title = $("#podinfo h1")[0].innerHTML;

        var state = {
          "context": response,
          "title": title,
        };

        $("title")[0].innerText = title;
        history.pushState(state, "", url);
      });
  })
  // go to home view
  .on("click", ".index-link", function(e) {
    e.preventDefault();
    goToIndex("search");
  })
  // open browse
  .on("click", ".browse-link", function(e) {
    e.preventDefault();
    goToIndex("browse");
   })
  .on("click", ".search-toggle", function(e) {
    e.preventDefault();
    toggleBars();
  })
  // open subscriptions
  .on("click", ".subscriptions-link", function(e) {
    e.preventDefault();
    goToIndex("subs");
  })
  // open settings in modal
  .on("click", ".settings-link", function(e) {
    e.preventDefault();
    goToIndex("settings");
  })
  // save settings, empty and hide modal
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
        $("#results").html(xhr.responseJSON.html);
      })
      .done(function(response) {
        goToIndex("search");
        loadContent("/charts/");
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
        $("#footer").css("padding-bottom", "106px");
      });
  })
  // close player
  .on("click", "#player-close", function(e) {
    $("#player").empty();
    $("#footer").css("padding-bottom", "0px");
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
        goToModal("/account/login/");
      })
      .done(function(response) {
        button.html(response);

        var url = $("#main-content")[0].baseURI;
        var context = $("#main-content")[0].innerHTML;
        if ($("#podinfo").length) {
          var title = $("#podinfo h1")[0].innerHTML;
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
    goToModal(url);
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
        $("#modal-content").html(xhr.responseJSON.html);
      })
      .done(function() {
        $("#modal-content").html("");
        $("#modal").modal("hide");
        refreshCookie();
        refreshPage();
        loadContent("/charts/");
      });
  })
