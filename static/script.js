const copyIcons = document.querySelectorAll('#project-detail img');

function moveCursorToEnd(el) {
  if (typeof el.selectionStart == "number") {
    el.selectionStart = el.selectionEnd = el.value.length;
  } else if (typeof el.createTextRange != "undefined") {
    el.focus();
    let range = el.createTextRange();
    range.collapse(false);
    range.select();
  }
}

function copyToClipboard(elem) {
  let textElem = elem.parentElement.previousElementSibling;
  let range = document.createRange();
  range.selectNode(textElem);
  window.getSelection().removeAllRanges(); 
  window.getSelection().addRange(range); 
  document.execCommand("copy");
  window.getSelection().removeAllRanges();
  showNotification()
}

function showNotification() {
  let message = 'Copied!';
  if (document.cookie.indexOf('django_language=ru') != -1) {
    message = 'Скопировано!'
  }
  const n = document.createElement('div')
  n.classList.add('notification')
  n.innerText = message
  notify.appendChild(n)
  setTimeout(() => {
      n.remove()
  }, 2000)
}
