# 🚀 GAURANGA - Deploy Guide

## Opsi 1: GitHub Pages (Butuh Setingan Manual)

### Step 1: Buat Repo Public
```
1. Buka: https://github.com/prahlad168/Alpha-agent-Gaurangga/settings
2. Scroll ke "Danger Zone"
3. Klik "Change visibility"
4. Pilih "Make public"
5. Konfirmasi
```

### Step 2: Enable GitHub Pages
```
1. Settings → Pages
2. Source: Deploy from branch
3. Branch: main, folder: /android-app
4. Save
```

### Step 3: Tunggu 2-5 menit
Buka: https://prahlad168.github.io/Alpha-agent-Gaurangga/android-app/

---

## Opsi 2: Netlify (Instant!)

1. Buka: https://app.netlify.com/drop
2. Drag folder `android-app` ke browser
3. Dapat URL langsung!

---

## Opsi 3: Vercel

```bash
npm i -g vercel
cd android-app
vercel
```

---

## Opsi 4: Local Server

```bash
cd android-app
python3 -m http.server 8080
# Buka: http://localhost:8080
```

---

## 📱 Download sebagai APK (Android)

1. Serve folder android-app
2. Buka di Chrome HP
3. Klik "Add to Home Screen"

---

**URL setelah deploy:**
https://prahlad168.github.io/Alpha-agent-Gaurangga/android-app/
