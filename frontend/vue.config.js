module.exports = {
  devServer: {
    proxy: {
      "/": {
        target: "http://localhost:5000",
        changeOrigin: true,
        secure: false,
        cookieDomainRewrite: "localhost",
        ws: false,
      },
    },
  },
  publicPath: "/",
};
