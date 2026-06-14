#!/usr/bin/env python3
import http.server
import socketserver
import urllib.request
import urllib.error
import os
import json
from pathlib import Path

FRONTEND_DIR = Path(__file__).parent / "frontend" / "dist"
BACKEND_URL = "http://127.0.0.1:5000"

INJECT_SCRIPT = """
<script>
(function() {
  const API_BASE = "http://127.0.0.1:5000/api";

  async function httpGet(path) {
    const res = await fetch(API_BASE + path);
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "请求失败");
    return data;
  }

  const parkingApi = {
    getDailyRevenue: () => httpGet("/parking/revenue/daily")
  };

  const BarChart3Icon = {
    name: "BarChart3Icon",
    iconNode: [
      ["path", {d: "M3 3v18h18", key: "1svgic"}],
      ["path", {d: "M18 17V9", key: "16y1ck"}],
      ["path", {d: "M13 17V5", key: "1wqttg"}],
      ["path", {d: "M8 17v-3", key: "17mjqa"}]
    ]
  };

  function createIconComponent(iconDef) {
    return {
      name: iconDef.name,
      props: ['size', 'strokeWidth'],
      setup(props) {
        const size = Vue.computed(() => props.size || 24);
        const strokeWidth = Vue.computed(() => props.strokeWidth || 2);
        return () => {
          const h = Vue.h;
          return h('svg', {
            xmlns: "http://www.w3.org/2000/svg",
            width: size.value,
            height: size.value,
            viewBox: "0 0 24 24",
            fill: "none",
            stroke: "currentColor",
            "stroke-width": strokeWidth.value,
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            class: "lucide lucide-" + iconDef.name.toLowerCase()
          }, iconDef.iconNode.map(node => h(node[0], node[1])));
        };
      }
    };
  }

  const StatGrid = {
    name: 'StatGrid',
    props: ['stats'],
    setup(props) {
      return () => {
        const h = Vue.h;
        return h('div', { class: 'stat-grid' },
          props.stats.map(stat =>
            h('section', { class: 'stat-card', key: stat.label }, [
              h('span', stat.label),
              h('strong', stat.value)
            ])
          )
        );
      };
    }
  };

  const RevenueDashboardPage = {
    name: 'RevenueDashboardPage',
    setup() {
      const ref = Vue.ref;
      const computed = Vue.computed;
      const onMounted = Vue.onMounted;
      const h = Vue.h;

      const dailyRevenue = ref([]);
      const loading = ref(false);
      const error = ref('');

      const summaryStats = computed(() => {
        const total = dailyRevenue.value.reduce(
          (acc, item) => ({
            amount: acc.amount + item.total_amount,
            orders: acc.orders + item.order_count,
            free: acc.free + item.free_count,
          }),
          { amount: 0, orders: 0, free: 0 }
        );
        return [
          { label: '累计结算金额', value: '¥' + total.amount.toFixed(2) },
          { label: '累计订单数', value: total.orders },
          { label: '累计免费车辆', value: total.free },
          { label: '统计天数', value: dailyRevenue.value.length },
        ];
      });

      async function loadRevenue() {
        loading.value = true;
        error.value = '';
        try {
          const data = await parkingApi.getDailyRevenue();
          dailyRevenue.value = data.items;
        } catch (err) {
          error.value = err.message;
        } finally {
          loading.value = false;
        }
      }

      onMounted(loadRevenue);

      return () => h('div', { class: 'page-stack' }, [
        h('header', { class: 'page-header' }, [
          h('div', [
            h('h2', '日营收看板'),
            h('p', '按日期查看结算金额、免费车辆、订单数量和高峰时段。')
          ]),
          h('button', {
            class: 'primary-button',
            type: 'button',
            onClick: loadRevenue
          }, '刷新')
        ]),
        h(StatGrid, { stats: summaryStats.value }),
        error.value ? h('p', { class: 'error-text' }, error.value) : null,
        h('section', { class: 'table-section' }, [
          h('h3', '每日营收明细'),
          h('div', { class: 'table-wrap' }, [
            h('table', [
              h('thead', [
                h('tr', [
                  h('th', '日期'),
                  h('th', '结算金额'),
                  h('th', '免费车辆'),
                  h('th', '订单数量'),
                  h('th', '高峰时段')
                ])
              ]),
              h('tbody', { class: loading.value ? 'muted' : '' },
                dailyRevenue.value.length > 0
                  ? dailyRevenue.value.map(item =>
                      h('tr', { key: item.date }, [
                        h('td', item.date),
                        h('td', [h('strong', '¥' + item.total_amount.toFixed(2))]),
                        h('td', item.free_count + ' 辆'),
                        h('td', item.order_count + ' 单'),
                        h('td', item.peak_hour)
                      ])
                    )
                  : loading.value
                    ? []
                    : [h('tr', [
                        h('td', {
                          colspan: 5,
                          style: 'text-align: center; color: #65746e;'
                        }, '暂无结算数据')
                      ])]
              )
            ])
          ])
        ])
      ]);
    }
  };

  const BarChart3 = createIconComponent(BarChart3Icon);

  function injectRevenueTab() {
    const nav = document.querySelector('.sidebar nav');
    if (!nav) {
      setTimeout(injectRevenueTab, 100);
      return;
    }

    const existingTabs = nav.querySelectorAll('button');
    let revenueTabExists = false;
    existingTabs.forEach(btn => {
      if (btn.textContent && btn.textContent.includes('日营收')) {
        revenueTabExists = true;
      }
    });

    if (revenueTabExists) return;

    const tabs = Array.from(existingTabs);
    let billingIndex = -1;
    tabs.forEach((tab, idx) => {
      if (tab.textContent && tab.textContent.includes('临停')) {
        billingIndex = idx;
      }
    });

    const newTab = document.createElement('button');
    newTab.type = 'button';
    newTab.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-barchart3icon"><path d="M3 3v18h18"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg><span>日营收看板</span>';

    const contentPanel = document.querySelector('.content-panel');
    newTab.addEventListener('click', function() {
      tabs.forEach(t => t.classList.remove('active'));
      newTab.classList.add('active');
      if (contentPanel) {
        contentPanel.innerHTML = '';
        const app = Vue.createApp(RevenueDashboardPage);
        app.mount(contentPanel);
      }
    });

    if (billingIndex >= 0 && billingIndex + 1 < tabs.length) {
      tabs[billingIndex + 1].before(newTab);
    } else {
      nav.appendChild(newTab);
    }

    const api = window.parkingApi || {};
    api.getDailyRevenue = parkingApi.getDailyRevenue;
    window.parkingApi = api;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectRevenueTab);
  } else {
    injectRevenueTab();
  }
})();
</script>
"""

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self.proxy_request()
            return

        if self.path == "/" or self.path == "/index.html":
            self.serve_index_with_injection()
            return

        super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self.proxy_request()
            return
        self.send_error(404)

    def do_PATCH(self):
        if self.path.startswith("/api/"):
            self.proxy_request()
            return
        self.send_error(404)

    def proxy_request(self):
        try:
            url = BACKEND_URL + self.path
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None

            req = urllib.request.Request(url, data=body, method=self.command)
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'content-length']:
                    req.add_header(header, value)

            with urllib.request.urlopen(req, timeout=10) as response:
                self.send_response(response.status)
                for header, value in response.headers.items():
                    if header.lower() not in ['transfer-encoding', 'connection']:
                        self.send_header(header, value)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_error(500, str(e))

    def serve_index_with_injection(self):
        index_path = FRONTEND_DIR / "index.html"
        if not index_path.exists():
            self.send_error(404)
            return

        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace('</body>', INJECT_SCRIPT + '</body>')

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == "__main__":
    PORT = 8080
    with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
        print(f"Server running at http://127.0.0.1:{PORT}")
        print(f"Frontend: {FRONTEND_DIR}")
        print(f"Backend proxy: {BACKEND_URL}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
