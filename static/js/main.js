function copyToClipboard(text) {
  const elem = document.createElement('textarea');
  elem.value = text;
  document.body.appendChild(elem);
  elem.select();
  document.execCommand('copy');
  document.body.removeChild(elem);
}

function notify(msg, type){
  if (document.querySelector('.notification'))
    return 

  const colors = {success: 'bg-green-700', failed: 'bg-red-700', error: 'bg-red-700'}
  const color = colors[type]
  const elm = document.createElement('div')
  const classes = `notification fixed ${color} py-3 px-5 text-center right-0 bottom-10 w-32 capitalize text-white font-bold opacity-70 transition transform translate-x-full`
  elm.setAttribute('class', classes)
  elm.innerText = msg

  document.body.appendChild(elm)
  setTimeout(() => {
    elm.classList.remove('translate-x-full')
    setTimeout(() => {
      elm.classList.add('translate-x-full')
      setTimeout(() => {
        elm.remove()
      }, 100)
    }, 1200)
  }, 100)
  
}

function escapeHTML(unsafeText) {
  let div = document.createElement('div');
  div.innerText = unsafeText;
  return div.innerHTML;
}

function toHTML(text, forceSpace=true){
  let t =  text // escapeHTML(text);
  t = t.replace(/\n/g, '<br>')
  if (forceSpace)
    t = t.replace(/ /g, '&nbsp;')
  return t
}

function setButtonLink(){
  // alert('set urls')
  document.querySelectorAll('button[role="link"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const href = e.target.dataset.href
      const a = document.createElement('a')
      a.href = href
      a.style.cssText = "opacity: 0;"
      document.body.appendChild(a)
      a.click()
      a.remove()
    })
  })
}
