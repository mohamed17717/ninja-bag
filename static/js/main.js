function copyToClipboard(text) {
  const elem = document.createElement("textarea");
  elem.value = text;
  document.body.appendChild(elem);
  elem.select();
  document.execCommand("copy");
  document.body.removeChild(elem);
}

function notify(msg, type) {
  if (document.querySelector(".notification")) return;

  const colors = {
    success: "bg-green-700",
    failed: "bg-red-700",
    error: "bg-red-700",
  };
  const color = colors[type];
  const elm = document.createElement("div");
  const classes = `notification fixed ${color} py-3 px-5 text-center right-0 bottom-10 capitalize text-white font-bold opacity-70 transition transform translate-x-full z-10`;
  elm.setAttribute("class", classes);
  elm.innerText = msg;

  document.body.appendChild(elm);
  setTimeout(() => {
    elm.classList.remove("translate-x-full");
    setTimeout(() => {
      elm.classList.add("translate-x-full");
      setTimeout(() => {
        elm.remove();
      }, 100);
    }, 2000);
  }, 100);
}

function escapeHTML(unsafeText) {
  let div = document.createElement("div");
  div.innerText = unsafeText;
  return div.innerHTML;
}

function toHTML(text, forceSpace = true) {
  let t = text; // escapeHTML(text);
  t = t.replace(/\n/g, "<br>");
  if (forceSpace) t = t.replace(/ /g, "&nbsp;");
  return t;
}

function setButtonLink() {
  // alert('set urls')
  document.querySelectorAll('button[role="link"]').forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const href = e.target.dataset.href;
      const a = document.createElement("a");
      a.href = href;
      a.style.cssText = "opacity: 0;";
      document.body.appendChild(a);
      a.click();
      a.remove();
    });
  });
}

function readBackendJsonById(elmId) {
  return JSON.parse(document.getElementById(elmId).textContent);
}

function htmlToText(html) {
  const elm = document.createElement("div");
  elm.innerHTML = html;
  return elm.innerText;
}

function isFormValid(form) {
  const inputs = form.querySelectorAll("input");
  for (let input of inputs) {
    const isInputValid = input.checkValidity();
    if (!isInputValid) {
      notify(`input ${input.name} is not valid`, "error");
      return false;
    }
  }
  return true;
}
