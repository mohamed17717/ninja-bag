function renderEndpoints() {
  console.log('this is data object')
  let endpoints = JSON.parse(djangoEndpoints).map(item => ({
    ...item, isOpen: false, popup: false,
    httpSyntaxHeader: '', httpSyntaxBody: ''
  }))

  return {
    endpoints,
    getMethodColor(endpoint){
      const method = endpoint.method.toLowerCase()
      const colors = {
        get: 'bg-green-700',
        post: 'bg-yellow-700',
        delete: 'bg-red-700',
      }
      return colors[method]
    },

    checkLimitExist(endpoint, limit){
      const limits = endpoint.limits
      return limits && limits.includes(limit)
    },

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

    isHttpHasBody(endpoint) {
      return endpoint.method === 'POST' && endpoint.params && endpoint.params.POST.length
    },

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
      const ref = Math.random().toString(36).slice(-5)
      const alpineCode = ` x-ref="${ref}" @change="inputChange(endpoints, $refs['${ref}'])"`
      return `class="${klass}" name="${param.name}" type="${type}" value="${value}" ${accept} ${required}`
    },

    inputChange(endpoint, elm) {
      console.log(endpoint)
      console.log(elm, elm.value)
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
      }

      return httpBody
    },

    getHttpSyntax (endpoint, forceUpdate=false) {
      if (endpoint.httpSyntaxHeader.length && !forceUpdate) return

      endpoint.httpSyntaxHeader = this.getHttpSyntaxHeader(endpoint)
      if(this.isHttpHasBody)
        endpoint.httpSyntaxBody = this.getHttpSyntaxBody(endpoint)
    },

    getHttpSyntaxHeader(endpoint) {
      return toHTML(this.generateHttpHeaderSyntax(endpoint))
    },
    getHttpSyntaxBody(endpoint) {
      return toHTML(this.generateHttpBodySyntax(endpoint), endpoint.dataType === 'json')
    },
  }
}
