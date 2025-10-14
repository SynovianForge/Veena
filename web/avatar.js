// web/avatar.js
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { VRMLoaderPlugin } from "@pixiv/three-vrm";

const canvas = document.getElementById("avatarCanvas");

// === Renderer ===
const renderer = new THREE.WebGLRenderer({
  canvas,
  alpha: true,
  antialias: true
});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(canvas.clientWidth, canvas.clientHeight);
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.setClearColor(0x000000, 0); // transparent background

// === Scene & Camera ===
const scene = new THREE.Scene();
scene.background = null;

const camera = new THREE.PerspectiveCamera(
  35,
  canvas.clientWidth / canvas.clientHeight,
  0.1,
  20
);

// Pull back slightly and lower height for better framing
camera.position.set(0.11, 1.15, 1.7);

// === Lighting ===
const ambient = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambient);

const dir = new THREE.DirectionalLight(0xffffff, 1);
dir.position.set(0.5, 1, 2);
dir.castShadow = true;
scene.add(dir);

let currentVrm = null;
const clock = new THREE.Clock();

// === Load VRM ===
const loader = new GLTFLoader();
loader.register((parser) => new VRMLoaderPlugin(parser));

loader.load(
  "./models/model.vrm",
  (gltf) => {
    const vrm = gltf.userData.vrm;
    currentVrm = vrm;
    scene.add(vrm.scene);
    if (vrm) {

      // Center model and face camera
      vrm.scene.rotation.y = 0;
      vrm.scene.position.set(0, 0, 0);

      // Optional: scale if too large or small
      vrm.scene.scale.set(1, 1, 1);

      scene.add(vrm.scene);
      console.log("✅ VRM model loaded:", vrm);
    } else {
      console.error("⚠️ VRM object missing in gltf.userData!");
    }
  },
  (progress) => {
    const pct = ((progress.loaded / progress.total) * 100).toFixed(1);
    console.log(`Loading VRM: ${pct}%`);
  },
  (error) => console.error("❌ VRM load error:", error)
);

// === Animate ===
function animate() {
  requestAnimationFrame(animate);
  const delta = clock.getDelta();

  if (currentVrm) {
    const t = Date.now() * 0.001;

    // Subtle idle movement: slow head sway
    const head = currentVrm.humanoid?.getNormalizedBoneNode("head");
    if (head) head.rotation.y = Math.sin(t) * 0.1;

    // Light breathing motion
    const chest = currentVrm.humanoid?.getNormalizedBoneNode("chest");
    if (chest) chest.position.y = 0.02 * Math.sin(t * 1.5);

    currentVrm.update(delta);
  }

  renderer.render(scene, camera);
}
animate();

// === Resize handling ===
window.addEventListener("resize", () => {
  camera.aspect = canvas.clientWidth / canvas.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(canvas.clientWidth, canvas.clientHeight);
});
