function refresh_page() {
  // refresh navbar (and maybe other stuff as well?)
  $.ajax({
    type: "GET",
    url: "navbar/",
    error: function(xhr, ajaxOptions, thrownError){alert(thrownError);},
    success: function(response) {
      // refresh navbar
      $(".nav-content").html(response);
      // TODO go to index
    }
  });
}
