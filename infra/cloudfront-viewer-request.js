// CloudFront Function (cloudfront-js-2.0), viewer-request.
// Purposes:
//   1. Canonicalize www.qodeh.com -> qodeh.com (301, preserving path+query).
//   2. Serve Hugo pretty URLs from S3: "/x/" -> "/x/index.html".
//   3. Add the trailing slash Hugo's canonical URLs use: "/x" -> "/x/" (301)
//      for extensionless paths, so S3 object lookup and canonical URLs agree.
function handler(event) {
    var request = event.request;
    var host = request.headers.host && request.headers.host.value;

    if (host === 'www.qodeh.com') {
        var qs = '';
        var keys = Object.keys(request.querystring);
        if (keys.length > 0) {
            var parts = [];
            for (var i = 0; i < keys.length; i++) {
                var k = keys[i];
                if (request.querystring[k].multiValue) {
                    request.querystring[k].multiValue.forEach(function (mv) {
                        parts.push(k + '=' + mv.value);
                    });
                } else if (request.querystring[k].value === '') {
                    parts.push(k);
                } else {
                    parts.push(k + '=' + request.querystring[k].value);
                }
            }
            qs = '?' + parts.join('&');
        }
        return {
            statusCode: 301,
            statusDescription: 'Moved Permanently',
            headers: {
                location: { value: 'https://qodeh.com' + request.uri + qs }
            }
        };
    }

    var uri = request.uri;
    if (uri.endsWith('/')) {
        request.uri = uri + 'index.html';
    } else if (!uri.includes('.')) {
        return {
            statusCode: 301,
            statusDescription: 'Moved Permanently',
            headers: { location: { value: uri + '/' } }
        };
    }
    return request;
}
