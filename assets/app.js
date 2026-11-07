// Shared by every page: header state, sign-in, and calls to the server.

export const API = "https://pdf-occlusion-api.pdf-occlusion.workers.dev";
export const ANKIWEB = "https://ankiweb.net/shared/info/783821131";

const FIREBASE = {
  apiKey: "AIzaSyCGLpF7okQTqHrGU-AE_6NWp8w1BdlO8T8",
  authDomain: "pdf-occlusion.github.io",
  projectId: "pdf-occlusion-57036",
  appId: "1:553099909371:web:68c60a14c074a3dc1ff85e",
};
const SDK = "https://www.gstatic.com/firebasejs/10.12.2";

let authPromise = null;
async function auth() {
  if (!authPromise) {
    authPromise = (async () => {
      const { initializeApp } = await import(`${SDK}/firebase-app.js`);
      const a = await import(`${SDK}/firebase-auth.js`);
      const app = initializeApp(FIREBASE);
      return { lib: a, auth: a.getAuth(app) };
    })();
  }
  return authPromise;
}

// Calls back with the signed-in user, or null, now and on every change.
export async function watchUser(cb) {
  const { lib, auth: au } = await auth();
  lib.onAuthStateChanged(au, cb);
}

export async function signIn() {
  const { lib, auth: au } = await auth();
  const provider = new lib.GoogleAuthProvider();
  provider.setCustomParameters({ prompt: "select_account" });
  try {
    await lib.signInWithPopup(au, provider);
  } catch (e) {
    // popups blocked (some mobile browsers): fall back to a full-page redirect
    if (e && (e.code === "auth/popup-blocked" || e.code === "auth/operation-not-supported-in-this-environment")) {
      await lib.signInWithRedirect(au, provider);
    } else if (e && e.code !== "auth/popup-closed-by-user" && e.code !== "auth/cancelled-popup-request") {
      throw e;
    }
  }
}

export async function signOut() {
  const { lib, auth: au } = await auth();
  await lib.signOut(au);
}

// Removes the Google sign-in itself too. Firebase only allows that soon
// after signing in, so a stale session just signs out instead.
export async function deleteSignIn() {
  const { lib, auth: au } = await auth();
  try { if (au.currentUser) await lib.deleteUser(au.currentUser); }
  catch { await lib.signOut(au); }
}

export async function api(path, { method = "GET", body, user } = {}) {
  const headers = { "content-type": "application/json" };
  if (user) headers.authorization = `Bearer ${await user.getIdToken()}`;
  const res = await fetch(API + path, { method, headers, body: body ? JSON.stringify(body) : undefined });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(data.error || `Request failed (${res.status})`);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

export function when(ms) {
  const d = new Date(ms);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

