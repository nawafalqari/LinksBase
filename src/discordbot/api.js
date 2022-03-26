const fetch = require('node-fetch')

const api_url = 'https://api.linksb.me'

async function get(username) {
    let res = await fetch(`${api_url}/user/${username}`)
    let data = await res.json()
    return data
}

async function get_qrcode(username) {
    let res = await fetch(`${api_url}/qrcode/${username}`)
    let data = await res.json()
    return data
}

module.exports = {
    'get': get,
    'get_qrcode': get_qrcode
}