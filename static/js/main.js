$(document).ready(function () {

   const navbar = $("#mainNavbar");
   const toggler = $(".navbar-toggler");

   toggler.removeClass("menu-open");

   navbar.on("show.bs.collapse", function () {
      $("body").addClass("nav-open");
      toggler.addClass("menu-open");
   });

   navbar.on("hide.bs.collapse", function () {
      $("body").removeClass("nav-open");
      toggler.removeClass("menu-open");
   });

   $(window).on("scroll", function () {
      if ($(window).scrollTop() > 20) {
         $(".site-navbar").addClass("navbar-scrolled");
      } else {
         $(".site-navbar").removeClass("navbar-scrolled");
      }
   });



   const currentPath = window.location.pathname;

   $(".site-navbar .nav-link").each(function () {
      const linkPath = new URL(this.href).pathname;

      if (linkPath === currentPath) {
         $(this).addClass("active");
      } else {
         $(this).removeClass("active");
      }
   });

});