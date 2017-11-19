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

function goHome() {
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
      $("#site-content").fadeIn();
      var title = "dopepod";
      var state = {
        "context": response,
        "title": title,
      };
      history.pushState(state, "", url);
      $("title")[0].innerText = title;
    });
};

function goBrowse() {
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
      var title = "dopepod";
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
      // TODO go to index
      // REPETITION
      goHome();
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
  var genre = $("input[name='genre-button']:checked").val();
  var language = $("input[name='language-button']:checked").val();
  var explicit = $("input[name='explicit-button']").is(":checked");
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
  var abc = $("input[name='alphabet-button']:checked").val();
  var genre = $("input[name='genre-button']:checked").val();
  var language = $("input[name='language-button']:checked").val();
  var explicit = $("input[name='explicit-button']").is(":checked");
  var show = 25;
  $.ajax({
    method: "GET",
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
  // search when user types into search field (with min "delay" between keypresses)
  .on("keyup", "#q", debounce(SearchFunc, delay))
  // search when "search" button is clicked
  .on("submit", "#search-form", function (e) {
   e.preventDefault();
   debounce(SearchFunc, delay);
  })
  // search when user changes options
  .on("change", ".genre-buttons, .language-buttons, .explicit-buttons", SearchFunc)
  .on("change", ".alphabet-buttons", BrowseFunc)
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

        // load tracks for podcast
        // TODO also load on back button
        var url = "/tracks/";
        $.ajax({
          method: "POST",
          url: url,
          data: {
            "itunesid": itunesid,
          },
        })
          .fail(function(xhr, ajaxOptions, thrownError){
            console.log(thrownError);
          })
          .done(function(response) {
            $("#tracks").hide();
            $("#tracks").html(response);
            $('#overlay').addClass('hide');
            $("#tracks").fadeIn();
          });
      });
  })
  // open login or register in modal
  .on("click", ".ajax-login, .ajax-register", function(e) {
    e.preventDefault();
    var url = this.href;
    var method = this.method;
    $.ajax({
      type: method,
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError){
        console.log(thrownError);
      })
      .done(function(response) {
        $(".modal-content").html(response.html);
      });
  })
  // go to home view
  .on("click", ".home", function(e) {
    e.preventDefault();
    goHome();
  })
  // open settings in modal
  .on("click", ".settings", function(e) {
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
        $(".modal-content").html(response);
      });
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
        $(".modal-content").html(xhr.responseJSON.html);
      })
      .done(function(response) {
        $(".modal-content").html("");
        $("#modal").modal("hide");
      });
  })
  // open subscriptions
  .on("click", ".subscriptions", function(e) {
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
        var title = "subscriptions";
        var state = {
          "context": response,
          "title": title,
        };
        history.pushState(state, "", url);
        $("#site-content").hide();
        $("#site-content").html(response);
        $("#site-content").fadeIn();
        $("title")[0].innerText = title;
  });
})
  // open browse
  .on("click", ".browse", function(e) {
    e.preventDefault();
    goBrowse();
  })
  // put track in player
  .on("click", ".play", function(e) {
    e.preventDefault();
    var url = this.id;
    var type = this.name;
    $.ajax({
      method: "POST",
      url: "/play/",
      data: {
        "url": url,
        "type": type,
      },
    })
      .fail(function(xhr, ajaxOptions, thrownError){
        console.log(thrownError);
      })
      .done(function(response) {
        console.log("whadup");
        $("#player").hide();
        $("#player").html(response);
        $("#player").fadeIn();
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
  // login or signup link (in modal)
  .on("click", ".login-link, .signup-link", function(e) {
    e.preventDefault();
    var url = this.href;
    $.ajax({
      url: url,
    })
      .fail(function(xhr, ajaxOptions, thrownError){
        console.log(thrownError);
      })
      .done(function(response) {
        $(".modal-content").html(response.html);
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
        $(".modal-content").html(xhr.responseJSON.html);
      })
      .done(function() {
        $(".modal-content").html("");
        $("#modal").modal("hide");
        refreshCookie();
        refreshPage();
      });
  })
  // logout, refresh after
  .on("click", ".ajax-logout", function(e) {
    e.preventDefault();
    $.ajax({
      type: "POST",
      url: "/account/logout/",
    })
      .fail(function(xhr, ajaxOptions, thrownError){
        console.log(thrownError);
      })
      .done(function() {
        refreshCookie();
        refreshPage();
      });
  });
