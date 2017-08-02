// "prepend event" functionality as a jQuery plugin
$.fn.extend({
  prependEvent: function (event, handler) {
    return this.each(function () {
      var events = $(this).data("events"), 
          currentHandler;

      if (events && events[event].length > 0) {
        currentHandler = events[event][0].handler;
        events[event][0].handler = function () {
          handler.apply(this, arguments);
          currentHandler.apply(this, arguments);
        }      
      }
    });
  }
});

