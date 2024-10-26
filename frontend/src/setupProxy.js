const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
  app.use(
    '/video-to-frames', // specify the path you want to proxy
    createProxyMiddleware({
      target: 'http://79.117.18.84:3841',
      changeOrigin: true,
    })
  );
};