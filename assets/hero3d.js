// 3D scene (classic script so it also works when the page is opened from disk).
// 3D scene for the home hero: a liquid-metal blob with an iridescent film, glass bubbles around it,
// a glass ring and floating particles. three.js comes from a CDN; without WebGL, or with reduced
// motion, the CSS orb stays (reduced motion still gets one still frame).

(function () {
const THREE = window.THREE;

const NOISE = `
  vec3 mod289(vec3 x){return x-floor(x*(1.0/289.0))*289.0;}
  vec4 mod289(vec4 x){return x-floor(x*(1.0/289.0))*289.0;}
  vec4 permute(vec4 x){return mod289(((x*34.0)+1.0)*x);}
  vec4 taylorInvSqrt(vec4 r){return 1.79284291400159-0.85373472095314*r;}
  float snoise(vec3 v){
    const vec2 C=vec2(1.0/6.0,1.0/3.0); const vec4 D=vec4(0.0,0.5,1.0,2.0);
    vec3 i=floor(v+dot(v,C.yyy)); vec3 x0=v-i+dot(i,C.xxx);
    vec3 g=step(x0.yzx,x0.xyz); vec3 l=1.0-g; vec3 i1=min(g.xyz,l.zxy); vec3 i2=max(g.xyz,l.zxy);
    vec3 x1=x0-i1+C.xxx; vec3 x2=x0-i2+C.yyy; vec3 x3=x0-D.yyy; i=mod289(i);
    vec4 p=permute(permute(permute(i.z+vec4(0.0,i1.z,i2.z,1.0))+i.y+vec4(0.0,i1.y,i2.y,1.0))+i.x+vec4(0.0,i1.x,i2.x,1.0));
    float n_=0.142857142857; vec3 ns=n_*D.wyz-D.xzx; vec4 j=p-49.0*floor(p*ns.z*ns.z);
    vec4 x_=floor(j*ns.z); vec4 y_=floor(j-7.0*x_); vec4 x=x_*ns.x+ns.yyyy; vec4 y=y_*ns.x+ns.yyyy; vec4 h=1.0-abs(x)-abs(y);
    vec4 b0=vec4(x.xy,y.xy); vec4 b1=vec4(x.zw,y.zw); vec4 s0=floor(b0)*2.0+1.0; vec4 s1=floor(b1)*2.0+1.0; vec4 sh=-step(h,vec4(0.0));
    vec4 a0=b0.xzyw+s0.xzyw*sh.xxyy; vec4 a1=b1.xzyw+s1.xzyw*sh.zzww;
    vec3 p0=vec3(a0.xy,h.x); vec3 p1=vec3(a0.zw,h.y); vec3 p2=vec3(a1.xy,h.z); vec3 p3=vec3(a1.zw,h.w);
    vec4 norm=taylorInvSqrt(vec4(dot(p0,p0),dot(p1,p1),dot(p2,p2),dot(p3,p3))); p0*=norm.x; p1*=norm.y; p2*=norm.z; p3*=norm.w;
    vec4 m=max(0.6-vec4(dot(x0,x0),dot(x1,x1),dot(x2,x2),dot(x3,x3)),0.0); m=m*m;
    return 42.0*dot(m*m,vec4(dot(p0,x0),dot(p1,x1),dot(p2,x2),dot(p3,x3)));
  }`;

// thin-film colour + fake studio reflections, shared by the blob and the bubbles
const SHADE = `
  vec3 film(float t){ float k=0.5+0.5*sin(6.28318*t); float j=0.5+0.5*sin(6.28318*t*1.7+1.3); return mix(mix(vec3(1.0,0.86,0.42), vec3(1.0,0.52,0.20), k), vec3(1.0,0.30,0.40), j*0.55); }
  vec3 studio(vec3 r){
    float top = smoothstep(0.2, 0.9, r.y);
    float side = pow(max(dot(r, normalize(vec3(-0.8,0.3,0.5))),0.0), 12.0);
    float rim = pow(max(dot(r, normalize(vec3(0.9,-0.2,0.4))),0.0), 8.0);
    vec3 col = mix(vec3(0.10,0.04,0.02), vec3(1.0,0.66,0.32), top);
    col += vec3(1.0)*side*1.4 + vec3(1.0,0.35,0.30)*rim*0.9;
    col += vec3(1.0,0.82,0.35)*smoothstep(-0.2,-0.9,r.y)*0.35;
    return col;
  }`;

function init(canvas) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'low-power' });
  } catch (e) { return; }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  document.documentElement.classList.add('has-3d');

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(36, 1, 0.1, 100);
  camera.position.set(0, 0.2, 9);
  const root = new THREE.Group();
  scene.add(root);

  // ---- liquid metal blob ----
  const blobMat = new THREE.ShaderMaterial({
    uniforms: { uTime: { value: 0 }, uAmp: { value: 0.32 } },
    vertexShader: NOISE + `
      uniform float uTime; uniform float uAmp;
      varying vec3 vN; varying vec3 vView; varying float vD;
      float field(vec3 p){ return snoise(p*0.9 + vec3(0.0, uTime*0.35, uTime*0.22)) * uAmp
                                  + snoise(p*2.1 - uTime*0.3) * uAmp*0.35; }
      void main(){
        vec3 p = position; vec3 n = normalize(normal);
        float d = field(p); vD = d;
        // numeric normal from neighbouring points on the displaced surface
        vec3 t = normalize(cross(n, vec3(0.0,1.0,0.0) + 0.0001)); vec3 b = normalize(cross(n, t));
        float e = 0.02;
        vec3 pt = p + t*e; vec3 pb = p + b*e;
        vec3 P  = p  + n*d;
        vec3 PT = pt + normalize(pt)*field(pt);
        vec3 PB = pb + normalize(pb)*field(pb);
        vec3 nn = normalize(cross(PT-P, PB-P));
        if (dot(nn, n) < 0.0) nn = -nn;
        vec4 mv = modelViewMatrix * vec4(P,1.0);
        vN = normalize(normalMatrix * nn); vView = normalize(-mv.xyz);
        gl_Position = projectionMatrix * mv;
      }`,
    fragmentShader: SHADE + `
      uniform float uTime; varying vec3 vN; varying vec3 vView; varying float vD;
      void main(){
        vec3 n = normalize(vN); vec3 v = normalize(vView);
        float fres = pow(1.0 - max(dot(n,v),0.0), 2.5);
        vec3 r = reflect(-v, n);
        vec3 metal = studio(r) * vec3(1.0,0.90,0.78);
        vec3 irid = film(fres*1.2 + vD*1.5 + uTime*0.05);
        vec3 col = mix(metal, metal*0.55 + irid*0.75, 0.35 + fres*0.55);
        col += irid * fres * 0.6;
        gl_FragColor = vec4(col, 1.0);
      }`,
  });
  const blob = new THREE.Mesh(new THREE.IcosahedronGeometry(1.55, 64), blobMat);
  root.add(blob);

  // ---- glass bubbles ----
  const glassMat = new THREE.ShaderMaterial({
    uniforms: { uTime: { value: 0 } },
    transparent: true, depthWrite: false,
    vertexShader: `varying vec3 vN; varying vec3 vView;
      void main(){ vec4 mv = modelViewMatrix*vec4(position,1.0); vN = normalize(normalMatrix*normal); vView = normalize(-mv.xyz); gl_Position = projectionMatrix*mv; }`,
    fragmentShader: SHADE + `
      uniform float uTime; varying vec3 vN; varying vec3 vView;
      void main(){
        vec3 n=normalize(vN); vec3 v=normalize(vView);
        float fres = pow(1.0-max(dot(n,v),0.0), 2.0);
        vec3 col = studio(reflect(-v,n))*0.8 + film(fres*1.6 + uTime*0.04)*fres;
        float spec = pow(max(dot(reflect(-v,n), normalize(vec3(-0.5,0.7,0.6))),0.0), 40.0);
        gl_FragColor = vec4(col + spec, 0.08 + fres*0.75 + spec);
      }`,
  });
  const bubbles = [];
  [[2.6, 0.9, 0.42, 0.0], [-2.7, -0.4, 0.3, 2.1], [1.9, -1.6, 0.22, 4.0], [-1.6, 1.8, 0.18, 1.0], [3.1, -0.9, 0.12, 3.0], [-3.2, 1.1, 0.1, 5.0]]
    .forEach(([x, y, r, ph]) => {
      const m = new THREE.Mesh(new THREE.SphereGeometry(r, 48, 48), glassMat);
      m.position.set(x, y, (Math.random() - 0.5) * 1.5);
      root.add(m);
      bubbles.push({ m, x, y, ph });
    });

  // ---- glass ring ----
  const ring = new THREE.Mesh(new THREE.TorusGeometry(2.55, 0.05, 32, 220), glassMat);
  const ringG = new THREE.Group();
  ringG.rotation.set(-1.15, 0.2, 0.4);
  ringG.add(ring);
  const ring2 = new THREE.Mesh(new THREE.TorusGeometry(3.1, 0.018, 16, 220), glassMat);
  ring2.rotation.set(0.25, 0.1, 0);
  ringG.add(ring2);
  root.add(ringG);

  // ---- particles ----
  const N = 700;
  const pos = new Float32Array(N * 3);
  const col = new Float32Array(N * 3);
  const palette = [new THREE.Color('#ffd166'), new THREE.Color('#ff8a3d'), new THREE.Color('#ff4d6d'), new THREE.Color('#ffffff')];
  for (let i = 0; i < N; i++) {
    const rr = 3 + Math.random() * 8, th = Math.random() * Math.PI * 2, ph = Math.acos(2 * Math.random() - 1);
    pos.set([rr * Math.sin(ph) * Math.cos(th), rr * Math.cos(ph) * 0.6, rr * Math.sin(ph) * Math.sin(th) - 2], i * 3);
    const c = palette[i % 4];
    col.set([c.r, c.g, c.b], i * 3);
  }
  const pg = new THREE.BufferGeometry();
  pg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  pg.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const dot = document.createElement('canvas'); dot.width = dot.height = 64;
  const dg = dot.getContext('2d'); const grd = dg.createRadialGradient(32, 32, 0, 32, 32, 32);
  grd.addColorStop(0, 'rgba(255,255,255,1)'); grd.addColorStop(1, 'rgba(255,255,255,0)'); dg.fillStyle = grd; dg.fillRect(0, 0, 64, 64);
  const dust = new THREE.Points(pg, new THREE.PointsMaterial({ size: 0.05, map: new THREE.CanvasTexture(dot), vertexColors: true, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending, depthWrite: false }));
  scene.add(dust);

  // ---- interaction ----
  const target = { x: 0, y: 0 }, cur = { x: 0, y: 0 };
  let pulse = 0;
  addEventListener('pointermove', (e) => { target.x = (e.clientX / innerWidth - 0.5) * 2; target.y = (e.clientY / innerHeight - 0.5) * 2; }, { passive: true });
  addEventListener('pointerdown', () => { pulse = 1; }, { passive: true });

  function resize() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(canvas);
  resize();

  let visible = true, running = false;
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; if (visible && !reduce) loop(); }).observe(canvas);
  const clock = new THREE.Clock();

  function frame() {
    const t = clock.getElapsedTime();
    pulse *= 0.94;
    blobMat.uniforms.uTime.value = t;
    blobMat.uniforms.uAmp.value = 0.3 + Math.sin(t * 0.7) * 0.06 + pulse * 0.35;
    glassMat.uniforms.uTime.value = t;
    blob.rotation.y = t * 0.15;
    blob.rotation.x = Math.sin(t * 0.2) * 0.2;
    ring.rotation.z = t * 0.25;
    ring2.rotation.z = -t * 0.12;
    bubbles.forEach((b, i) => {
      b.m.position.x = b.x + Math.sin(t * 0.5 + b.ph) * 0.25;
      b.m.position.y = b.y + Math.cos(t * 0.6 + b.ph) * 0.3;
      b.m.rotation.y = t * 0.3 + i;
    });
    dust.rotation.y = t * 0.025;
    cur.x += (target.x - cur.x) * 0.04;
    cur.y += (target.y - cur.y) * 0.04;
    const s = Math.min(scrollY / 600, 1);
    root.rotation.y = cur.x * 0.4;
    root.rotation.x = cur.y * 0.25 + s * 0.4;
    root.position.y = s * 0.9;
    camera.position.x = cur.x * 0.5;
    camera.lookAt(0, 0, 0);
    renderer.render(scene, camera);
  }
  function loop() {
    if (running) return;
    running = true;
    const tick = () => {
      if (!visible || document.hidden) { running = false; return; }
      frame();
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }
  document.addEventListener('visibilitychange', () => { if (!document.hidden && !reduce) loop(); });
  frame();
  if (!reduce) loop();
}
const canvas = document.getElementById('hero3d');
if (canvas && THREE) init(canvas);
})();
