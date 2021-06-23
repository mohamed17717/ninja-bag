let paramsDataStore = {}

// function setChangeEventOnForminput (formId) {
//   const form = document.querySelector(`#${formId}`)
//   form.querySelectorAll('input').forEach(input => {
//     console.log('change', input)
//     input.addEventListener('click', e => {
//       console.log('changed')
//       console.log(e.target.value)
//       console.log(paramsDataStore)
//     })
//   })
// }

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

function getHttpSyntaxBodyForm(formSyntax) {
  const match = formSyntax.match(/id="([\w-]+?)"/)
  if(match === null) return

  const formId = match[1]
  const form = document.querySelector(`#${formId}`)
  console.log('gotm: ', form)
  let serializedForm
  if(isFormValid(form))
    serializedForm = new FormData(form)
  return serializedForm

}

function getHttpSyntaxBodyJson(bodySyntax) {
  console.log(bodySyntax)

  const bodyText = htmlToText(bodySyntax.replace(/\&nbsp\;/g, ''))
  console.log(bodyText)

  return bodyText
}


function renderEndpoints() {
  console.log('this is data object')
  let endpoints = JSON.parse(djangoEndpoints).map(item => ({
    ...item, isOpen: false, 
    popup: false, popupInfo: {
      isLoading: true,
      url: '',method: '',body: '',headers: '', 
      response: {code: 0, html: '', type: '', blobUrl: '', blobHasView: false}
    },
    httpSyntaxHeader: '', httpSyntaxBody: ''
  }))

  return {
    endpoints,

    getMethodColor(method){
      const colors = {
        get: 'bg-green-700',
        post: 'bg-yellow-700',
        delete: 'bg-red-700',
      }
      return colors[method.toLowerCase()]
    },

    checkLimitExist(endpoint, limit){
      const limits = endpoint.limits
      return limits && limits.includes(limit)
    },

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

    // http syntax -- body
    isHttpHasBody(endpoint) {
      return endpoint.method === 'POST' && endpoint.params && endpoint.params.POST.length
    },

    // http syntax -- body -- form
    getParamInputAtributes (param) {
      const paramName = param.name
      console.log('paramINputAttribute')
      const value = paramsDataStore[paramName] || param.default || ''
      const acceptImage = 'accept="image/png, image/jpeg"'
      const required = param.required ? 'required' : ''

      let type = param.type
      let accept = ''

      if(type === 'image') {
        accept = acceptImage
        type = 'file'
      }

      const klass = type === 'file' ? 'mb-2' : 'mb-2 text-primary-700'
      const ref = Math.random().toString(36).slice(-5)
      const eventName = type === 'file' ? 'change' : 'keyup'
      const alpineCode = `x-ref="${ref}" @${eventName}="inputChange('${param.name}', $refs['${ref}'])"`
      return `class="${klass}" name="${param.name}" type="${type}" value="${value}" ${accept} ${required} ${alpineCode}`
    },

    inputChange(paramName, elm) {
      // handle file later
      console.log('change')
      const name = elm.name
      const value = elm.value
      paramsDataStore[name] = value
      console.log(paramsDataStore)
    },

    generateHttpBodySyntax (endpoint) {
      console.log('generate HTTP body')
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
      if(this.isHttpHasBody)
        endpoint.httpSyntaxBody = this.getHttpSyntaxBody(endpoint)
    },


    // action buttons
    resetHttpSyntax (endpoint) {
      getHttpSyntax(endpoint, true)
    },

    runRequest(endpoint) {
      const httpSyntaxHeader = endpoint.httpSyntaxHeader
                                .replace(/&amp;/g, '&')
                                .replace(/<br>/g, '\n')
                                .replace(/&nbsp;/g, ' ')

      let invalidRequest = false

      // -_* step 1 - get path and set values in the url
      let httpSyntaxHeaderPath = httpSyntaxHeader
                                  .split('\n').shift() // first line
                                  .split(' ').slice(1, -1).join(' ')

      let [pathPart, getPart] = httpSyntaxHeaderPath.split('?')
      let pathParams = pathPart.match(/\{[\w ]+\}/g) || []
      let getParams = getPart && getPart.match(/\{[\w ]+\}/g) || []

      pathParams.forEach(param => {
        const endpointUrlParam = endpoint.params.URL.filter(p => `{${p.name}}` === param).pop()
        const paramDefault = endpointUrlParam && endpointUrlParam.default

        if(paramDefault !== undefined)
          pathPart = pathPart.replace(param, paramDefault)
        else // param is not exist or param is file or param has no default value 
          invalidRequest = true
      })

      getParams.forEach(param => {
        const endpointGetParam = endpoint.params.GET && endpoint.params.GET.filter(p => `{${p.name}}` === param).pop()
        const paramDefault = endpointGetParam && endpointGetParam.default

        if(paramDefault !== undefined)
          getPart = getPart.replace(param, paramDefault)
        // else // param is not exist or param is file or param has no default value 
        //   invalidRequest = true
      })

      getPart = (getPart || '').split('&').filter(i => i)
      getPart.push(`token=${userToken}`) // if token required else handle empty get part
      getPart = `?${getPart.join('&')}`

      let url = `${window.location.protocol}//${window.location.host}${pathPart}${getPart}` // set token
      if(invalidRequest) return
      console.log(url)
      // -_* step 2 - get method
      let method = httpSyntaxHeader.split(' ').shift()
      invalidRequest = endpoint.method !== method 
      if(invalidRequest) return
      console.log(method)
      // -_* step 3 - get http headers 
      let httpHeadersLines = httpSyntaxHeader
                          .replace(/<\/*?\w+?.+?>/gm, '\n')
                          .split('\n').slice(1)
                          .filter(i => i)
      let headers = {}
      httpHeadersLines.forEach(line => {
        let [name, value] = line.split(':')
        headers[name.trim()] = value.trim()
      })

      delete headers['Content-Type']
      console.log(headers)
      // -_* step 4 - get the body if exist and set the defualt if value is null

      const body = endpoint.dataType === 'json' ? 
        getHttpSyntaxBodyJson(endpoint.httpSyntaxBody): getHttpSyntaxBodyForm(endpoint.httpSyntaxBody)
      console.log('body: ', body)
      if(this.isHttpHasBody(endpoint) && body === undefined) return


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
      console.log('run fetch')
      fetch(url, { method, body, headers })
        .then(res => {
          endpoint.popupInfo.response.code = res.status
          endpoint.popupInfo.response.type = res.statusText

          console.log('this is response header: ', res.headers)
          // return res.text()
          return res.blob()
        })
        .then((blob) => {
          const resStatusText = endpoint.popupInfo.response.type
          const fileUrl = URL.createObjectURL(blob)
          endpoint.popupInfo.response.blobUrl = fileUrl
          if(fileUrl) {
            endpoint.popupInfo.response.type = `${resStatusText} (${blob.type})`
            endpoint.popupInfo.response.blobHasView = blob.size > 0
          }
          // endpoint.popupInfo.response.html = blob
          console.log(blob)
        })
        .catch(err => {
          console.log(err)
        })
        .finally(() => {
          endpoint.popupInfo.isLoading = false
          console.log('finally')
        })


      console.log('valid')
      return null
    },

    showEndpointInfo(endpoint) {
      if(endpoint.isOpen){
        endpoint.isOpen=false
      } else {
        this.endpoints.forEach(e => e.isOpen=false)
        endpoint.isOpen = true
      }
    }
  }
}
