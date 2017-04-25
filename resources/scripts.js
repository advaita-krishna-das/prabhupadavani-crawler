window.onkeypress = function(e) {
  key = e.keyCode || e.which;
  if (key == 104) {
    var selection = window.getSelection();
    var range = selection.getRangeAt(0);
    var newNode = document.createElement("span");
    newNode.setAttribute("style", "background-color: pink;");
    range.surroundContents(newNode);
  }
}
