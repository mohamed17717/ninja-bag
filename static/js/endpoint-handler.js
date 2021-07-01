function htmlToText(html) {
  const elm = document.createElement('div')
  elm.innerHTML = html
  return elm.innerText
}

function isFormValid(form){
  const inputs = form.querySelectorAll('input')
  for(let input of inputs){
    const isInputValid = input.checkValidity()
    if(! isInputValid){
      notify(`input ${input.name} is not valid`, 'error')
      return false
    }
  }
  return true
}


function renderEndpoints() {
  let endpoints = JSON.parse(djangoEndpoints).map(ep => Endpoint.generate(ep))

  return {
    endpoints,

    // http syntax -- header
    getHttpHeaderContentType(endpoint) {
      const dataType = endpoint.dataType
      const dataTypeMap = {
        // application/x-www-form-urlencoded
        form: 'Content-Type: multipart/form-data', 
        json: 'Content-Type: application/json',
      }

      return dataTypeMap[dataType] || ''
    },

    generateHttpHeaderSyntax (endpoint){
      const method = endpoint.method.toUpperCase()
      const path = endpoint.url // maybe later i need to add GET prams to it
      const httpContentType = this.getHttpHeaderContentType(endpoint)
      const httpVersion = 'HTTP/1.1'

      return `${method} ${path} ${httpVersion}\n${httpContentType}`.trim()
    },

    // http syntax -- body -- form
    getParamInputAtributes (param) {
      const value = param.default || ''
      const acceptImage = 'accept="image/png, image/jpeg"'
      const required = param.required ? 'required' : ''

      let type = param.type
      let accept = ''

      if(type === 'image') {
        accept = acceptImage
        type = 'file'
      }

      const klass = type === 'file' ? 'mb-2' : 'mb-2 text-primary-700'
      return `class="${klass}" name="${param.name}" type="${type}" value="${value}" ${accept} ${required}`
    },

    generateHttpBodySyntax (endpoint) {
      const dataType = endpoint.dataType // json | form
      let httpBody = ''

      if(dataType === 'json'){
        httpBodyJson = {}
        endpoint.params.POST.map(param =>
          httpBodyJson[param.name] = param.default )

        httpBody = JSON.stringify(httpBodyJson, null, 2)
      } else if (dataType === 'form') {
        endpoint.params.POST.map(param => {
          const inputAttributes = this.getParamInputAtributes(param)
          httpBody += `${param.name}: <input ${inputAttributes}> <br>`
        })

        const formId = `form-id-${Math.random().toString(36).slice(-5)}`
        httpBody = `<form @submit.prevent="console.log('run')" id="${formId}">${ httpBody }</form>`
        // setTimeout(() => setChangeEventOnForminput(formId), 100)
      }

      return httpBody
    },

    getHttpSyntaxHeader(endpoint) {
      return toHTML(this.generateHttpHeaderSyntax(endpoint))
    },
    getHttpSyntaxBody(endpoint) {
      const forceAllSpaces = endpoint.dataType === 'json'
      return toHTML(this.generateHttpBodySyntax(endpoint), forceAllSpaces)
    },

    getHttpSyntax (endpoint, forceUpdate=false) {
      if (endpoint.httpSyntaxHeader.length && !forceUpdate) return

      endpoint.httpSyntaxHeader = this.getHttpSyntaxHeader(endpoint)
      if(Endpoint.isHttpHasBody(endpoint))
        endpoint.httpSyntaxBody = this.getHttpSyntaxBody(endpoint)
    },

    // action buttons
    resetHttpSyntax (endpoint) {
      this.getHttpSyntax(endpoint, true)
    },

    runRequest(endpoint) {
      const httpParser = new HTTPSyntaxParser(endpoint)

      // -_* step 1 - get path and set values in the url
      let url = httpParser.getUrl()
      if(!url) {
        notify('invalid url', 'error')
        return
      }
      // -_* step 2 - get method
      let method = httpParser.getMethod()
      if(!method) {
        notify(`Method not matched`, 'error')
        return
      }
      // -_* step 3 - get http headers 
      let headers = httpParser.getHeaders()
      // -_* step 4 - get the body if exist and set the defualt if value is null
      const body = httpParser.getBody()
      if(Endpoint.isHttpHasBody(endpoint) && body === undefined) {
        notify(`invalid syntax body`, 'error')
        return
      }
      // -_* step 5 - open popup -- send request -- show response
      endpoint.popupInfo.url = url
      endpoint.popupInfo.method = method
      endpoint.popupInfo.body = body
      endpoint.popupInfo.headers = headers
      endpoint.popupInfo.response.html = ''
      endpoint.popupInfo.response.type = ''
      endpoint.popupInfo.response.blobUrl = ''
      endpoint.popupInfo.response.blobHasView = false
      endpoint.popupInfo.response.code = 0
      endpoint.popupInfo.isLoading = true
      endpoint.popup = true
      // -_* step 6 - send request
      fetch(url, { method, body, headers })
        .then(res => {
          endpoint.popupInfo.response.code = res.status
          endpoint.popupInfo.response.type = res.statusText

          return res.blob()
        })
        .then((blob) => {
          const resStatusText = endpoint.popupInfo.response.type

          endpoint.popupInfo.response.blobUrl = URL.createObjectURL(blob)
          endpoint.popupInfo.response.type = `${resStatusText} (${blob.type})`
          endpoint.popupInfo.response.blobHasView = blob.size > 0
        })
        .catch(err => console.error(err))
        .finally(() => endpoint.popupInfo.isLoading = false )
    },

    showEndpointInfo(endpoint) {
      if(endpoint.isOpen){
        endpoint.isOpen = false
      } else {
        this.endpoints.forEach(e => e.isOpen = false)
        endpoint.isOpen = true
      }
    }
  }
}
