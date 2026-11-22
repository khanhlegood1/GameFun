/*! @game9k/game-sdk — bản tham chiếu, tương thích 1:1 với Poki SDK.
 *
 *  Đây là mã THAM CHIẾU để `scripts/check_sdk.py` có thứ để đếm và để studio
 *  đọc được toàn bộ bề mặt trong một lần. Bản phát hành thật sẽ được dựng từ
 *  `packages/game-sdk` (docs/06 M03) với cùng hợp đồng và cùng ngân sách.
 *
 *  Ba điều KHÔNG có trong tệp này, và đó là thiết kế:
 *    · không gọi mạng   — mọi thứ đi qua `postMessage` lên portal;
 *    · không đọc storage/cookie — docs/03 §3.2;
 *    · không có hàm thanh toán hay ký giao dịch — docs/27 §6 R2.
 */
(function (global) {
  'use strict';

  var P = global.parent;
  var W = global;
  var pending = {};
  var seq = 0;
  var env = null;      // 'inspector' | 'preview' | 'play' | 'arena' | 'direct'
  var versionLabel = undefined;
  var ready = false;

  // ---- PoP: chỉ đếm, không ghi nội dung (docs/PRD.md FR-SDK-01) ------------
  var pop = { input: 0, lastInputAt: 0, gaps: [], errors: 0, fps: 0 };

  function send(type, payload) {
    return new Promise(function (resolve) {
      var id = ++seq;
      var done = false;
      var timer = W.setTimeout(function () {
        if (!done) { done = true; delete pending[id]; resolve(null); }
      }, 4000);
      pending[id] = function (data) {
        if (done) return;
        done = true;
        W.clearTimeout(timer);
        resolve(data);
      };
      // `targetOrigin` là '*' ở đây vì SDK không tự biết origin của portal.
      // Portal mới là bên siết: nó kiểm `event.origin === origin của bản build`
      // (docs/03 §3 quy tắc 1). SDK không bao giờ tin bản tin nhận vào.
      P.postMessage({ __game9k: 1, id: id, type: type, payload: payload }, '*');
    });
  }

  W.addEventListener('message', function (e) {
    if (e.source !== P) return;                       // chỉ nghe portal
    var m = e.data;
    if (!m || m.__game9k !== 1) return;
    if (m.type === 'reply' && pending[m.id]) { pending[m.id](m.payload); delete pending[m.id]; }
    if (m.type === 'ping') send('pong', { at: m.at });
  });

  // ---- đo PoP, không đọc nội dung ----------------------------------------
  ['pointerdown', 'keydown', 'touchstart'].forEach(function (evt) {
    W.addEventListener(evt, function () {
      var now = Date.now();
      if (pop.lastInputAt) pop.gaps.push(now - pop.lastInputAt);
      if (pop.gaps.length > 200) pop.gaps.shift();
      pop.lastInputAt = now;
      pop.input++;                                   // chỉ đếm; event.key KHÔNG bị đọc
    }, { passive: true, capture: true });
  });
  W.addEventListener('error', function () { pop.errors++; });

  var frames = 0, fpsAt = Date.now();
  (function tick() {
    frames++;
    var now = Date.now();
    if (now - fpsAt >= 1000) {
      pop.fps = Math.round((frames * 1000) / (now - fpsAt));
      frames = 0; fpsAt = now;
    }
    if (W.requestAnimationFrame) W.requestAnimationFrame(tick);
  })();

  function entropy() {
    if (pop.gaps.length < 8) return 0;
    var buckets = {}, n = pop.gaps.length, i, b, p, h = 0;
    for (i = 0; i < n; i++) {
      b = pop.gaps[i] < 120 ? 'a' : pop.gaps[i] < 400 ? 'b' : pop.gaps[i] < 1200 ? 'c' : 'd';
      buckets[b] = (buckets[b] || 0) + 1;
    }
    for (b in buckets) { p = buckets[b] / n; h -= p * Math.log(p) / Math.LN2; }
    return Math.round(h * 100) / 100;
  }

  function beat() {
    if (!ready) return;
    send('pop', { input: pop.input, entropy: entropy(), errors: pop.errors, fps: pop.fps });
  }
  W.setInterval(beat, 30000);

  // ---- API công khai -----------------------------------------------------
  var SDK = {
    init: function () {
      return send('init', { ua_webgl: !!W.WebGLRenderingContext }).then(function (r) {
        env = (r && r.environment) || 'direct';
        versionLabel = r && r.versionLabel;   // arena: portal CỐ Ý không trả
        ready = true;
        return { environment: env, versionLabel: versionLabel };
      });
    },

    // 5 sự kiện Poki — đúng tên, đúng thứ tự (developers.poki.com/guide/sdk-overview)
    gameLoadingFinished: function () { send('gameLoadingFinished', { loadMs: W.performance ? Math.round(W.performance.now()) : 0 }); },
    gameplayStart: function () { send('gameplayStart', { at: Date.now() }); },
    gameplayStop: function () { send('gameplayStop', { at: Date.now() }); },

    commercialBreak: function (onStart) {
      // Arena và direct KHÔNG BAO GIỜ có quảng cáo: arena vì quảng cáo lộ thời
      // điểm (phá Blind Duel), direct vì lưu lượng studio tự kéo chịu 0% phí.
      if (env === 'arena' || env === 'direct' || env === 'inspector') {
        if (onStart) onStart();
        return Promise.resolve();
      }
      if (onStart) onStart();
      return send('commercialBreak', {}).then(function () { /* portal tự quyết có phát hay không */ });
    },

    rewardedBreak: function (opts) {
      if (env === 'arena' || env === 'direct' || env === 'inspector' || env === 'preview') {
        return Promise.resolve(false);   // không có quảng cáo thì không hứa quà
      }
      if (opts && opts.onStart) opts.onStart();
      return send('rewardedBreak', { size: (opts && opts.size) || 'medium' }).then(function (r) {
        return !!(r && r.rewarded);
      });
    },

    cloudSave: {
      get: function (slot) { return send('cloudSave.get', { slot: slot || 'default' }).then(function (r) { return r ? r.value : null; }); },
      set: function (value, slot) { return send('cloudSave.set', { slot: slot || 'default', value: value }).then(function () {}); }
    },

    // Không tự cấp token, không tự cộng SPARK: chỉ báo một mốc đã xảy ra.
    reportProgress: function (milestoneKey, numericValue) {
      send('reportProgress', { key: milestoneKey, value: numericValue === undefined ? 1 : numericValue });
    }
  };

  W.Game9KSDK = SDK;
  // Adapter để game viết cho Poki chạy nguyên: `PokiSDK.commercialBreak()`.
  if (!W.PokiSDK) W.PokiSDK = SDK;
})(typeof window !== 'undefined' ? window : this);
