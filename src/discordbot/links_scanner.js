const fetch = require('node-fetch')

let links_scanner_url = `https://ipqualityscore.com/api/json/url/${process.env.LINKS_SCANNER_API_KEY}`

function encodeURL(url) {
    for(i of url) {
        if(i === '/') {
            url = url.replcae('/', '%5C')
        }
    }

    return url
}

async function isSafe(url) {
    res = fetch(`${links_scanner_url}/${encodeURL(url)}`).json()

    if(res['unsafe']) return true
    return false
}

module.exports = isSafe