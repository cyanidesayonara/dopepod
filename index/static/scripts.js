$(window).on('popstate', function(event) {
  var state = event.originalEvent.state;
  if (state) {
    $("#site-content").hide();
    $("#site-content").html(state.context);
    $("#site-content").fadeIn();
    $("title")[0].innerText = state.title;
    if (state.q) {
      $("#q").val(state.q);
    }
    if (state.abc) {
      $("input[name='alphabet'][value='" + state.abc + "']").prop("checked", true);
    }
    if (state.show) {
      $("input[name='show'][value='" + state.show + "']").prop("checked", true);
    }
  }
});

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
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
  var csrftoken = getCookie('csrftoken');
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });
};

function goToHome() {
  var url = "/";
  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
      console.log(thrownError);
    })
    .done(function(response) {
      $("#site-content").hide();
      $("#site-content").html(response);
      $("#podinfo").ready(function() {
        $("#site-content").fadeIn();
      });
      var title = "dopepod";
      var state = {
        "context": response,
        "title": title,
      };
      history.pushState(state, "", url);
      $("title")[0].innerText = title;
    });
};

function goToBrowse() {
  var url = "/browse/";
  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      $("#site-content").hide();
      $("#site-content").html(response);
      $("#site-content").fadeIn();
      var title = "browse";
      var state = {
        "context": response,
        "title": title,
      };
      history.pushState(state, "", url);
      $("title")[0].innerText = title;
    });
};

function goToSubscriptions() {
  var url = "/subscriptions/";
  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      $("#site-content").hide();
      $("#site-content").html(response);
      $("#site-content").fadeIn();
      var title = "subscriptions";
      var state = {
        "context": response,
        "title": title,
      };
      history.pushState(state, "", url);
      $("title")[0].innerText = title;
    });
};

function goToSettings() {
  var url = "/settings/";
  $.ajax({
    type: "GET",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      $("#site-content").hide();
      $("#site-content").html(response);
      $("#site-content").fadeIn();
      var title = "settings";
      var state = {
        "context": response,
        "title": title,
      };
      history.pushState(state, "", url);
      $("title")[0].innerText = title;
    });
};

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
      goToHome();
    });
};

// wait until user stops typing
// credit: https://remysharp.com/2010/07/21/throttling-function-calls/
function debounce(fn, delay) {
  var timer = null;
  return function () {
    var context = this, args = arguments;
    clearTimeout(timer);
    timer = setTimeout(function () {
      fn.apply(context, args);
    }, delay);
  };
};

// ye ajax search function
function SearchFunc() {
  // minlength for search string
  var minlength = 2
  // gather variables
  var q = $("#site-content #q").val();
  var genre = $("input[name='search-genre']:checked").val();
  var language = $("input[name='search-language']:checked").val();
  var explicit = $("input[name='search-explicit']").is(":checked");
  // if input is at least minlength, go ahead and search
  if (q.length >= minlength) {
    $.ajax({
      method: "GET",
      url: "/search/",
      data: {
        "q": q,
        "genre": genre,
        "language": language,
        "explicit": explicit,
        // "show": show,
      },
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        console.log(thrownError);
      })
      .done(function(response) {
        $("#results").hide();
        $("#results").html(response);
        $("#results").fadeIn();
        // save results + q in current state
        // TODO results is still mostly hidden
        // removing style (hacky)
        $("#results").removeAttr("style");
        var curContext = $("#site-content")[0].innerHTML;
        var curUrl = $("#site-content")[0].baseURI;
        var curTitle = "dopepod";
        var curState = {
          "context": curContext,
          "title": curTitle,
          "q": q,
        };
        history.replaceState(curState, "", curUrl);
      });
  }
  // else show nothing
  else {
    $("#results").hide();
    $("#results").html("");
    $("#results").fadeIn();

    // save results + q in current state
    // TODO results is still mostly hidden
    // removing style (hacky)
    $("#results").removeAttr("style");
    var curContext = $("#site-content")[0].innerHTML;
    var curUrl = $("#site-content")[0].baseURI;
    var curTitle = "dopepod";
    var curState = {
      "context": curContext,
      "title": curTitle,
      "q": q,
    };
    history.replaceState(curState, "", curUrl);
  }
};

function BrowseFunc() {
  var abc = $("input[name='alphabet']:checked").val();
  var show = $("input[name='show']:checked").val();
  var genre = $("input[name='browse-genre']:checked").val();
  var language = $("input[name='browse-language']:checked").val();
  var explicit = $("input[name='browse-explicit-button']").is(":checked");
  $.ajax({
    method: "POST",
    url: "/browse/",
    data: {
      "abc": abc,
      "show": show,
      "genre": genre,
      "language": language,
      "explicit": explicit,
    },
  })
    .fail(function(xhr, ajaxOptions, thrownError) {
      console.log(thrownError);
    })
    .done(function(response) {
      $("#results").hide();
      $("#results").html(response);
      $("#results").fadeIn();

      // save results + q in current state
      // TODO results is still mostly hidden
      // removing style (hacky)
      $("#results").removeAttr("style");
      var curContext = $("#site-content")[0].innerHTML;
      var curUrl = $("#site-content")[0].baseURI;
      var curTitle = "dopepod";
      var curState = {
        "context": curContext,
        "title": curTitle,
        "abc": abc,
        "show": show,
      };
      history.replaceState(curState, "", curUrl);
    });
};

function getSubscriptions() {
  // load subscriptions
  var url = "/subscriptions/";
  $.ajax({
    type: "POST",
    url: url,
  })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      $("#subscriptions").html(response);
    });
};

var delay = 250

// after page loads
$(document)
  // refresh cookie
  .ready(refreshCookie())
  // initialize bootstrap tooltips
  .ready($('[data-toggle="tooltip"]').tooltip())
  // search when user types into search field (with min "delay" between keypresses)
  // .on("keyup", "#q", debounce(SearchFunc, delay))
  // search when "search" button is clicked
  // .on("submit", "#search-form", function (e) {
  //   e.preventDefault();
  //   SearchFunc();
  // })
  // remove focus from button (focus would be saved on state)
  .on("click", "#search-genre-buttons, #search-language-buttons, #search-explicit-buttons, #alphabet-buttons, #show-buttons, #browse-genre-buttons, #browse-language-buttons, #browse-explicit-buttons", function() {
    $(this.children).removeClass("focus");
  })
  // search when user changes options
  // .on("change", "#search-genre-buttons, #search-language-buttons, #search-explicit-buttons", SearchFunc)
  // browse when user changes options
  // .on("change", "#alphabet-buttons, #show-buttons, #browse-genre-buttons, #browse-language-buttons, #browse-explicit-buttons", BrowseFunc)
  // show podinfo
  .on("click", ".show-podinfo", function(e) {
    e.preventDefault();
    var url = this.href;
    var url2 = this.href;
    var itunesid = this.id;
    $.ajax({
      type: "GET",
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError) {
        console.log(thrownError);
      })
      .done(function(response) {
        $("#site-content").hide();
        $("#site-content").html(response);
        $("#site-content").fadeIn();

        var title = $(".podinfo h3")[0].innerHTML;
        var state = {
          "context": response,
          "title": title,
        };

        $("title")[0].innerText = title;
        history.pushState(state, "", url2);
      });
  })
  // go to home view
  .on("click", ".home", function(e) {
    e.preventDefault();
    goToHome();
  })
  // open browse
  .on("click", ".browse", function(e) {
    e.preventDefault();
    goToBrowse();
  })
  // open subscriptions
  .on("click", ".subscriptions", function(e) {
    e.preventDefault();
    goToSubscriptions();
  })
  // open settings in modal
  .on("click", ".settings", function(e) {
    e.preventDefault();
    goToSettings();
  })
  // save settings, empty and hide modal
  .on("submit", ".settings-form", function (e) {
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
        $("#site-content").html(xhr.responseJSON.html);
      })
      .done(function(response) {
        goToHome();
      });
  })
  // put track in player
  .on("click", ".play", function(e) {
    e.preventDefault();
    var url = this.id;
    var type = this.name;
    console.log(this);
    $.ajax({
      method: "POST",
      url: "/play/",
      data: {
        "url": url,
        "type": type,
        // "title": title,
      },
    })
      .fail(function(xhr, ajaxOptions, thrownError){
        console.log(thrownError);
      })
      .done(function(response) {
        $("#player").html(response);
      });
  })
  // TODO check if subscribed or nah
  // subscription button
  .on("submit", "#sub-form", function(e) {
    // Stop form from submitting normally
    e.preventDefault();
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
      })
      .done(function(data) {
        $("#sub-button").val(data);
      });
  })
  // open login register or password reset in modal
  .on("click", ".ajax-login, .ajax-register, .login-link, .signup-link, .password-link", function(e) {
    e.preventDefault();
    var url = this.href;
    $.ajax({
      type: "GET",
      url: url,
    })
    .fail(function(xhr, ajaxOptions, thrownError){
      console.log(thrownError);
    })
    .done(function(response) {
      $("#modal-content").html(response.html);
    });
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
      });
  })
  // logout, refresh after
  .on("click", ".ajax-logout", function(e) {
    e.preventDefault();
      var url = this.href;
    $.ajax({
      type: "POST",
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError){
        console.log(thrownError);
      })
      .done(function() {
        refreshPage();
      });
  });
