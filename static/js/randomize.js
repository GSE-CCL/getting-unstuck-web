// Shorthand for $( document ).ready()
$(function() {

    var $cards = $(".row-card");
    for(var i = 0; i < $cards.length; i++){
      var target = Math.floor(Math.random() * $cards.length -1) + 1;
      var target2 = Math.floor(Math.random() * $cards.length -1) +1;
      $cards.eq(target).before($cards.eq(target2));
    }


});