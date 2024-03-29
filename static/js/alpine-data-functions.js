const textareaAutoGrow = (elm, h) => {
  elm.style.height = h;
  elm.style.height = elm.scrollHeight + "px";
};

const closeDialogOnEscape = (thisObj, toggleKeyword) => {
  const close = (e) => {
    if (e.code === "Escape") thisObj[toggleKeyword] = false;
    if (thisObj[toggleKeyword] === false)
      document.removeEventListener("keyup", close);
  };

  document.addEventListener("keyup", close);
};

const sendRequestToBackend = (thisObj, descriptionName) => {
  const requestConfig = {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ description: thisObj[descriptionName] }),
  };

  fetch(thisObj.url, requestConfig)
    .then((res) => {
      thisObj['isButtonLoading'] = false;

      if (res.status < 250) {
        thisObj[descriptionName] = "";
        notify("Sent", "success");
      } else {
        return res.text();
      }
    })
    .then((text) => {
      if (text) notify(text, "failed");
    })
    .catch((err) => {
      console.error(err);
    });
}

const isValidDescription = (thisObj, descriptionName) => {
  thisObj['isButtonLoading'] = true;
  if (!thisObj[descriptionName].trim().length) {
    setTimeout(() => {
      thisObj['isButtonLoading'] = false;
    }, 1000);
    notify('can\'t send empty message.', 'failed')
    return false
  }

  return true
}

// data functions //

function toolSuggestionData() {
  return {
    url: suggestToolUrl,
    toolDescription: "",
    isButtonLoading: false,
    buttonStates: {
      loading: '<div class="lds-ripple"><div></div><div></div></div>',
      normal: "send",
    },

    textareaAutoGrow() {
      elm = this.$refs["suggestionTextarea"];
      textareaAutoGrow(elm, "6rem");
    },

    submitToolSuggestion() {
      const descriptionName = 'toolDescription'
      if(!isValidDescription(this, descriptionName))
        return

      sendRequestToBackend(this, descriptionName)
    },
  };
}

function toolIssueButtonData() {
  return {
    url: toolIssueUrl,
    issueDescription: "",
    isOpen: false,
    isButtonLoading: false,
    buttonStates: {
      loading:
        '<div class="lds-ripple" style="left:42%;"><div></div><div></div></div>',
      normal: "send",
    },

    closeDialogOnEscape() { closeDialogOnEscape(this, "isOpen"); },

    textareaAutoGrow() {
      elm = this.$refs["reportIssueTextarea"];
      textareaAutoGrow(elm, "8rem");
    },

    submitToolReport() {
      const descriptionName = 'issueDescription'
      if (!isValidDescription(this, descriptionName))
        return

      sendRequestToBackend(this, descriptionName)
    },
  };
}

function renderEndpoints() {
  let endpoints = readBackendJsonById("tool-endpoints").map((ep) =>
    Endpoint.generate(ep)
  );

  return {
    endpoints,

    // http syntax -- header
    getHttpHeaderContentType(endpoint) {
      const dataType = endpoint.dataType;
      const dataTypeMap = {
        // application/x-www-form-urlencoded
        form: "Content-Type: multipart/form-data",
        json: "Content-Type: application/json",
        text: "Content-Type: text/plain",
      };

      return dataTypeMap[dataType] || "";
    },

    generateHttpHeaderSyntax(endpoint) {
      const method = endpoint.method.toUpperCase();
      const path = endpoint.url; // maybe later i need to add GET prams to it
      const httpContentType = this.getHttpHeaderContentType(endpoint);
      const httpVersion = "HTTP/1.1";

      return `${method} ${path} ${httpVersion}\n${httpContentType}`.trim();
    },

    // http syntax -- body -- form
    getParamInputAtributes(param) {
      const value = param.default || "";
      const acceptImage = 'accept="image/png, image/jpeg"';
      const required = param.required ? "required" : "";

      let type = param.type;
      let accept = "";

      if (type === "image") {
        accept = acceptImage;
        type = "file";
      }

      const klass = type === "file" ? "mb-2" : "mb-2 text-primary-700";
      return `class="${klass}" name="${param.name}" type="${type}" value="${value}" ${accept} ${required}`;
    },

    generateHttpBodySyntax(endpoint) {
      const dataType = endpoint.dataType; // json | form | text
      let httpBody = "";

      if (dataType === "json") {
        httpBodyJson = {};
        endpoint.params.POST.map(
          (param) => (httpBodyJson[param.name] = param.default)
        );

        httpBody = JSON.stringify(httpBodyJson, null, 2);
      } else if (dataType === "form") {
        endpoint.params.POST.map((param) => {
          const inputAttributes = this.getParamInputAtributes(param);
          httpBody += `${param.name}: <input ${inputAttributes}> <br>`;
        });

        const formId = `form-id-${Math.random().toString(36).slice(-5)}`;
        httpBody = `<form @submit.prevent="console.log('run')" id="${formId}">${httpBody}</form>`;
        // setTimeout(() => setChangeEventOnForminput(formId), 100)
      } else if (dataType === "text") {
        httpBody = endpoint.defaultText;
      }

      console.log("dataType:", dataType);
      console.log("httpBody:", httpBody);

      return httpBody;
    },

    getHttpSyntaxHeader(endpoint) {
      return toHTML(this.generateHttpHeaderSyntax(endpoint));
    },
    getHttpSyntaxBody(endpoint) {
      console.log("this is body funcion");
      const forceAllSpaces =
        endpoint.dataType === "json" || endpoint.dataType === "text";
      return toHTML(this.generateHttpBodySyntax(endpoint), forceAllSpaces);
    },

    getHttpSyntax(endpoint, forceUpdate = false) {
      if (endpoint.httpSyntaxHeader.length && !forceUpdate) return;

      endpoint.httpSyntaxHeader = this.getHttpSyntaxHeader(endpoint);
      if (Endpoint.isHttpHasBody(endpoint))
        endpoint.httpSyntaxBody = this.getHttpSyntaxBody(endpoint);
    },

    // action buttons
    resetHttpSyntax(endpoint) {
      this.getHttpSyntax(endpoint, true);
    },

    setupPopupAndOpen(endpoint, popupInfo) {
      const { url, method, body, headers } = popupInfo;

      endpoint.popupInfo.url = url;
      endpoint.popupInfo.method = method;
      endpoint.popupInfo.body = body;
      endpoint.popupInfo.headers = headers;
      endpoint.popupInfo.response.html = "";
      endpoint.popupInfo.response.type = "";
      endpoint.popupInfo.response.blobUrl = "";
      endpoint.popupInfo.response.blobHasView = false;
      endpoint.popupInfo.response.code = 0;
      endpoint.popupInfo.isLoading = true;
      endpoint.popup = true;
    },

    closeDialogOnEscape(endpoint) { closeDialogOnEscape(endpoint, 'popup') },

    runRequest(endpoint) {
      this.closeDialogOnEscape(endpoint);
      const httpParser = new HTTPSyntaxParser(endpoint);

      // -_* step 1 - get path and set values in the url
      let url = httpParser.getUrl();
      if (!url) {
        notify("invalid url", "error");
        return;
      }
      // -_* step 2 - get method
      let method = httpParser.getMethod();
      if (!method) {
        notify(`Method not matched`, "error");
        return;
      }
      // -_* step 3 - get http headers
      let headers = httpParser.getHeaders();
      // -_* step 4 - get the body if exist and set the defualt if value is null
      const body = httpParser.getBody();
      if (Endpoint.isHttpHasBody(endpoint) && body === undefined) {
        notify(`invalid syntax body`, "error");
        return;
      }
      // -_* step 5 - open popup -- send request -- show response
      const popupInfo = { url, method, headers, body };
      this.setupPopupAndOpen(endpoint, popupInfo);
      // -_* step 6 - send request
      fetch(url, { method, body, headers })
        .then((res) => {
          endpoint.popupInfo.response.code = res.status;
          endpoint.popupInfo.response.type = res.statusText;

          return res.blob();
        })
        .then((blob) => {
          const resStatusText = endpoint.popupInfo.response.type;

          endpoint.popupInfo.response.blobUrl = URL.createObjectURL(blob);
          endpoint.popupInfo.response.type = `${resStatusText} (${blob.type})`;
          endpoint.popupInfo.response.blobHasView = blob.size > 0;
        })
        .catch((err) => console.error(err))
        .finally(() => (endpoint.popupInfo.isLoading = false));
    },

    showEndpointInfo(endpoint) {
      if (endpoint.isOpen) {
        endpoint.isOpen = false;
      } else {
        this.endpoints.forEach((e) => (e.isOpen = false));
        endpoint.isOpen = true;
      }
    },
  };
}

function getFooterData() {
  return {
    year: new Date().getFullYear(),
    author: "Mohamed Mahmoud",
    email: "d3v.mhmd@gmail.com",
    url: 'https://devmhmd.com',

    getAuthor() {
      return `<b><a href="mailto:${this.url}" target="_blank">${this.author}</a></b>`;
    },

    getPhrase() {
      return `© ${this.year} — Developed with ❤️ by ${this.getAuthor()}`;
    },
  };
}

function ToolDatabaseRecordsData() {
  return {
    confirmDelete (e) {
      const href = e.target.href
      if(confirm('Do you really wanna delete this file ? you will lose it forever.'))
        window.location.href = href
    },

    copyFileName(fileName) {
      copyToClipboard(fileName)
      notify('Copied', 'success')
    }
  }
}