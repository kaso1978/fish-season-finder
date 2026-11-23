#!/usr/bin/env node
/**
 * Zero-dependency static server for local development.
 *
 *   node serve.js [port]
 *
 * Use this rather than opening index.html from disk: browsers only grant
 * geolocation in a secure context, and http://localhost counts as secure
 * while a file:// path does not.
 */
const http = require('http');
const fs   = require('fs');
const path = require('path');

const port = Number(process.argv[2]) || 8000;
const root = __dirname;

const TYPES = {
  '.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8',
  '.css':'text/css; charset=utf-8',   '.json':'application/json; charset=utf-8',
  '.svg':'image/svg+xml',             '.png':'image/png',
  '.jpg':'image/jpeg',                '.ico':'image/x-icon',
  '.md':'text/plain; charset=utf-8', '.webmanifest':'application/manifest+json'
};

http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  let file = path.join(root, url === '/' ? 'index.html' : url);

  // Never serve anything outside the project directory.
  if (!path.resolve(file).startsWith(path.resolve(root))) {
    res.writeHead(403).end('Forbidden');
    return;
  }

  fs.stat(file, (err, stat) => {
    if (err || stat.isDirectory()) {
      res.writeHead(404, {'Content-Type':'text/plain'}).end('Not found');
      return;
    }
    res.writeHead(200, {
      'Content-Type': TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream',
      'Cache-Control': 'no-store'
    });
    fs.createReadStream(file).pipe(res);
  });
}).listen(port, () => {
  console.log('Fish Season Finder — http://localhost:' + port);
  console.log('Ctrl+C to stop.');
});
