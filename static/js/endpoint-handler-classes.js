class Endpoint {
  static generate(endpointObj) {
    const endpoint = {
      ...endpointObj,
      isOpen: false ,
      popup: false,
      popupInfo: {
        isLoading: true, url: '', method: '', body: '', headers: '',
        response: {
          code: 0, html: '', type: '', blobUrl: '', blobHasView: false
        }
      },
      httpSyntaxHeader: '',
      httpSyntaxBody: '',
    }

    return endpoint
  }

  static getMethodColor(endpoint){
    const method = endpoint.method.toLowerCase()
    const colors = {
      get: 'bg-green-700',
      post: 'bg-yellow-700',
      delete: 'bg-red-700',
    }

    const defaultColor = 'bg-blue-700'
    const color = colors[method] || defaultColor
    return color
  }

  static checkLimitExist(endpoint, limit){
    const limits = endpoint.limits
    return limits && limits.includes(limit)
  }

  static isHttpHasBody(endpoint) {
    return endpoint.method === 'POST' && endpoint.params && endpoint.params.POST.length
  }
}

class HTTPSyntaxParser {
  constructor(endpoint) {
    this.endpoint = endpoint
    this.httpHeader = endpoint.httpSyntaxHeader
        .replace(/&amp;/g, '&').replace(/<br>/g, '\n').replace(/&nbsp;/g, ' ')
    
  }

  #getHeaderPath () {
    const firstLine = this.httpHeader.split('\n').shift() 
    const parts = firstLine.split(' ').filter(i => i)

    let path
    if(parts.length >= 3)
      path = parts.slice(1, -1).join(' ')

    return path
  }

  #replacePathVariables(path, defaultParams) {
    let updatedPath = path
    let pathParams = path.match(/\{[\w ]+\}/g) || []
    pathParams.forEach(param => {
      const endpointUrlParam = defaultParams.filter(p => `{${p.name}}` === param).pop()
      const paramDefault = endpointUrlParam && endpointUrlParam.default

      if(paramDefault !== undefined)
        updatedPath = updatedPath.replace(param, paramDefault)
      else 
        return
    })

    return updatedPath
  }

  #replaceGETVariables(getPart, defaultParams, isToken) {
    let updatedGetPart = getPart
    let getParams = getPart && getPart.match(/\{[\w ]+\}/g) || []

    getParams.forEach(param => {
      const endpointGetParam = defaultParams && defaultParams.filter(p => `{${p.name}}` === param).pop()
      const paramDefault = endpointGetParam && endpointGetParam.default

      if(paramDefault !== undefined)
        updatedGetPart = updatedGetPart.replace(param, paramDefault)
    })

    if(isToken) {
      updatedGetPart = (updatedGetPart || '').split('&').filter(i => i)
      if(isLimitsActive) updatedGetPart.push(`token=${userToken}`)
      updatedGetPart = updatedGetPart.length > 0 ? `?${updatedGetPart.join('&')}` : ''
    }

    return updatedGetPart
  }

  getUrl () {
    let headerPath = this.#getHeaderPath()
    if(headerPath === undefined)
      return

    let [pathPart, getPart] = headerPath.split('?')

    if(this.endpoint.params && this.endpoint.params.URL)
      pathPart = this.#replacePathVariables(pathPart, this.endpoint.params.URL)

    if(this.endpoint.params && this.endpoint.params.GET)
      getPart = this.#replaceGETVariables(getPart, this.endpoint.params.GET, false)

    getPart = getPart || ''

    if(pathPart === undefined)
      return

    let url = `${window.location.protocol}//${window.location.host}${pathPart}${getPart}`
    return url
  }

  getMethod () {
    let method =  this.httpHeader.split(' ').shift()
    const isValidMethod = this.endpoint.method === method
    if (!isValidMethod)
      method = undefined
    return method
  }

  getHeaders () {
    let httpHeadersLines = this.httpHeader
        .replace(/<\/*?\w+?.+?>/gm, '\n')
        .split('\n').slice(1)
        .filter(i => i)

    let headers = {}
    httpHeadersLines.forEach(line => {
      let [name, value] = line.split(':')
      headers[name.trim()] = value.trim()
    })

    delete headers['Content-Type']
    return headers
  }

  #getHttpSyntaxBodyForm(formSyntax) {
    const match = formSyntax.match(/id="([\w-]+?)"/)
    if(match === null) return
  
    const formId = match[1]
    const form = document.querySelector(`#${formId}`)
  
    let serializedForm
    if(isFormValid(form))
      serializedForm = new FormData(form)
    return serializedForm
  
  }
  
  #getHttpSyntaxBodyJson(bodySyntax) {
    const bodyText = htmlToText(bodySyntax.replace(/\&nbsp\;/g, ''))
    return bodyText
  }

  getBody () {
    const httpBody = this.endpoint.httpSyntaxBody
    const body = this.endpoint.dataType === 'json' ? 
        this.#getHttpSyntaxBodyJson(httpBody) :
        this.#getHttpSyntaxBodyForm(httpBody)
    return body
  }
}
