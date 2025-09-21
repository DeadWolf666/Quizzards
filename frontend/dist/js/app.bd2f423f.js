(function () {
  "use strict";
  var n = {
      2381: function (n, t, o) {
        var e = o(3751),
          r = o(641);
        function a(n, t, o, e, a, i) {
          const s = (0, r.g2)("router-view");
          return (0, r.uX)(), (0, r.Wv)(s);
        }
        var i = { name: "App" },
          s = o(6262);
        const l = (0, s.A)(i, [["render", a]]);
        var u = l,
          c = o(5220);
        const d = { class: "container mt-5 text-center" };
        function m(n, t, o, e, a, i) {
          const s = (0, r.g2)("router-link");
          return (
            (0, r.uX)(),
            (0, r.CE)("div", d, [
              t[1] ||
                (t[1] = (0, r.Lk)("h1", null, "Welcome to Quizzards!", -1)),
              t[2] ||
                (t[2] = (0, r.Lk)("p", null, "This is the homepage.", -1)),
              (0, r.bF)(
                s,
                { class: "btn btn-primary", to: "/login" },
                {
                  default: (0, r.k6)(
                    () => t[0] || (t[0] = [(0, r.eW)("Login")])
                  ),
                  _: 1,
                  __: [0],
                }
              ),
            ])
          );
        }
        var f = { name: "HomeView" };
        const p = (0, s.A)(f, [["render", m]]);
        var h = p,
          v = o(33);
        const b = { class: "container mt-5", style: { "max-width": "400px" } },
          g = { class: "mb-3" },
          L = { class: "mb-3" },
          k = { key: 0, class: "alert alert-danger mt-3" };
        function w(n, t, o, a, i, s) {
          return (
            (0, r.uX)(),
            (0, r.CE)("div", b, [
              t[6] || (t[6] = (0, r.Lk)("h2", { class: "mb-4" }, "Login", -1)),
              (0, r.Lk)(
                "form",
                {
                  onSubmit:
                    t[2] ||
                    (t[2] = (0, e.D$)(
                      (...n) => s.handleLogin && s.handleLogin(...n),
                      ["prevent"]
                    )),
                },
                [
                  (0, r.Lk)("div", g, [
                    t[3] || (t[3] = (0, r.Lk)("label", null, "Email", -1)),
                    (0, r.bo)(
                      (0, r.Lk)(
                        "input",
                        {
                          "onUpdate:modelValue":
                            t[0] || (t[0] = (n) => (i.email = n)),
                          type: "email",
                          class: "form-control",
                          required: "",
                        },
                        null,
                        512
                      ),
                      [[e.Jo, i.email]]
                    ),
                  ]),
                  (0, r.Lk)("div", L, [
                    t[4] || (t[4] = (0, r.Lk)("label", null, "Password", -1)),
                    (0, r.bo)(
                      (0, r.Lk)(
                        "input",
                        {
                          "onUpdate:modelValue":
                            t[1] || (t[1] = (n) => (i.password = n)),
                          type: "password",
                          class: "form-control",
                          required: "",
                        },
                        null,
                        512
                      ),
                      [[e.Jo, i.password]]
                    ),
                  ]),
                  t[5] ||
                    (t[5] = (0, r.Lk)(
                      "button",
                      { type: "submit", class: "btn btn-success w-100" },
                      "Login",
                      -1
                    )),
                ],
                32
              ),
              i.error
                ? ((0, r.uX)(), (0, r.CE)("div", k, (0, v.v_)(i.error), 1))
                : (0, r.Q3)("", !0),
            ])
          );
        }
        o(4114);
        var y = {
          name: "LoginView",
          data() {
            return { email: "", password: "", error: "" };
          },
          methods: {
            async handleLogin() {
              this.error = "";
              try {
                const n = await fetch("/login", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    email: this.email,
                    password: this.password,
                  }),
                  credentials: "include",
                });
                if ((console.log("Login response status:", n.status), n.ok))
                  this.$router.push("/admin");
                else {
                  const t = await n.json();
                  this.error = t.error || "Login failed.";
                }
              } catch (n) {
                this.error = "Unable to connect to server.";
              }
            },
          },
        };
        const O = (0, s.A)(y, [["render", w]]);
        var A = O;
        const j = { class: "container mt-5" };
        function x(n, t, o, e, a, i) {
          return (
            (0, r.uX)(),
            (0, r.CE)("div", j, [
              t[1] || (t[1] = (0, r.Lk)("h2", null, "Admin Dashboard", -1)),
              t[2] || (t[2] = (0, r.Lk)("p", null, "Welcome, admin!", -1)),
              (0, r.Lk)(
                "button",
                {
                  onClick:
                    t[0] || (t[0] = (...n) => i.logout && i.logout(...n)),
                  class: "btn btn-danger mt-3",
                },
                "Logout"
              ),
            ])
          );
        }
        var C = {
          name: "AdminDashboard",
          methods: {
            async logout() {
              await fetch("/logout", {
                method: "POST",
                credentials: "include",
              }),
                this.$router.push("/");
            },
          },
        };
        const E = (0, s.A)(C, [["render", x]]);
        var T = E;
        const P = [
            { path: "/", name: "Home", component: h },
            { path: "/login", name: "Login", component: A },
            { path: "/admin", name: "AdminDashboard", component: T },
          ],
          X = (0, c.aE)({ history: (0, c.LA)(), routes: P });
        var D = X;
        const S = (0, e.Ef)(u);
        S.use(D), S.mount("#app");
      },
    },
    t = {};
  function o(e) {
    var r = t[e];
    if (void 0 !== r) return r.exports;
    var a = (t[e] = { exports: {} });
    return n[e].call(a.exports, a, a.exports, o), a.exports;
  }
  (o.m = n),
    (function () {
      var n = [];
      o.O = function (t, e, r, a) {
        if (!e) {
          var i = 1 / 0;
          for (c = 0; c < n.length; c++) {
            (e = n[c][0]), (r = n[c][1]), (a = n[c][2]);
            for (var s = !0, l = 0; l < e.length; l++)
              (!1 & a || i >= a) &&
              Object.keys(o.O).every(function (n) {
                return o.O[n](e[l]);
              })
                ? e.splice(l--, 1)
                : ((s = !1), a < i && (i = a));
            if (s) {
              n.splice(c--, 1);
              var u = r();
              void 0 !== u && (t = u);
            }
          }
          return t;
        }
        a = a || 0;
        for (var c = n.length; c > 0 && n[c - 1][2] > a; c--) n[c] = n[c - 1];
        n[c] = [e, r, a];
      };
    })(),
    (function () {
      o.d = function (n, t) {
        for (var e in t)
          o.o(t, e) &&
            !o.o(n, e) &&
            Object.defineProperty(n, e, { enumerable: !0, get: t[e] });
      };
    })(),
    (function () {
      o.g = (function () {
        if ("object" === typeof globalThis) return globalThis;
        try {
          return this || new Function("return this")();
        } catch (n) {
          if ("object" === typeof window) return window;
        }
      })();
    })(),
    (function () {
      o.o = function (n, t) {
        return Object.prototype.hasOwnProperty.call(n, t);
      };
    })(),
    (function () {
      var n = { 524: 0 };
      o.O.j = function (t) {
        return 0 === n[t];
      };
      var t = function (t, e) {
          var r,
            a,
            i = e[0],
            s = e[1],
            l = e[2],
            u = 0;
          if (
            i.some(function (t) {
              return 0 !== n[t];
            })
          ) {
            for (r in s) o.o(s, r) && (o.m[r] = s[r]);
            if (l) var c = l(o);
          }
          for (t && t(e); u < i.length; u++)
            (a = i[u]), o.o(n, a) && n[a] && n[a][0](), (n[a] = 0);
          return o.O(c);
        },
        e = (self["webpackChunkfrontend"] = self["webpackChunkfrontend"] || []);
      e.forEach(t.bind(null, 0)), (e.push = t.bind(null, e.push.bind(e)));
    })();
  var e = o.O(void 0, [504], function () {
    return o(2381);
  });
  e = o.O(e);
})();
//# sourceMappingURL=app.bd2f423f.js.map
