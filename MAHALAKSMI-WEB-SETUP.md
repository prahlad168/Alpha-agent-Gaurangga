# 🏠 Setup GAURANGA di mahalaksmi.web.id

## Opsi 1: Subdomain (gaurangga.mahalaksmi.web.id) ✅ RECOMMENDED

### Langkah 1: Update CNAME File
File `CNAME` sudah dibuat otomatis:
```
gaurangga.mahalaksmi.web.id
```

### Langkah 2: Setup DNS di Registrar Anda

Tambahkan record DNS berikut:

#### Untuk Cloudflare:
```
Type: CNAME
Name: gaurangga
Target: prahlad168.github.io
Proxy status: DNS only (grey cloud) ⚠️ IMPORTANT
```

#### Untuk Registrar Lain (Namecheap, GoDaddy, dll):
```
Type: CNAME
Host: gaurangga
Value: prahlad168.github.io
TTL: Auto / 1 Hour
```

### Langkah 3: Enable GitHub Pages Custom Domain

1. Buka https://github.com/prahlad168/Alpha-agent-Gaurangga/settings/pages
2. Pada "Custom domain", masukkan: `gaurangga.mahalaksmi.web.id`
3. Centang "Enforce HTTPS"
4. Save

### Langkah 4: Tunggu Propagasi
- DNS propagation: 5 menit - 48 jam
- Cek status: https://dnschecker.org/#CNAME/gaurangga.mahalaksmi.web.id

---

## Opsi 2: Redirect dari mahalaksmi.web.id

Jika Anda ingin GAURANGA tampil langsung di `mahalaksmi.web.id`:

### Untuk WordPress:
1. Install plugin "Redirection" atau "Simple 301 Redirects"
2. Tambahkan redirect:
   ```
   Source URL: /
   Target URL: https://prahlad168.github.io/Alpha-agent-Gaurangga/mahalaksmi-web.html
   ```

### Untuk cPanel:
1. Buka File Manager
2. Edit `index.html` di root
3. Tambahkan di `<head>`:
   ```html
   <meta http-equiv="refresh" content="0; url=https://prahlad168.github.io/Alpha-agent-Gaurangga/mahalaksmi-web.html">
   ```

### Untuk Nginx:
```nginx
location / {
    return 301 https://prahlad168.github.io/Alpha-agent-Gaurangga/mahalaksmi-web.html;
}
```

---

## Opsi 3: Iframe Embed (Tidak Direkomendasikan)

Jika Anda ingin GAURANGA tampil di dalam halaman mahalaksmi.web.id:

```html
<iframe 
    src="https://prahlad168.github.io/Alpha-agent-Gaurangga/mahalaksmi-web.html" 
    width="100%" 
    height="100vh" 
    frameborder="0">
</iframe>
```

⚠️ **Catatan**: Iframe mungkin tidak berfungsi dengan baik untuk semua fitur.

---

## ✅ Checklist Setup

- [ ] CNAME file sudah ada
- [ ] DNS record CNAME sudah ditambahkan
- [ ] GitHub Pages custom domain sudah di-set
- [ ] HTTPS sudah enforced
- [ ] Website sudah bisa diakses

---

## 🔗 Link Hasil

| Setup | URL |
|-------|-----|
| GitHub Pages Default | https://prahlad168.github.io/Alpha-agent-Gaurangga/ |
| Subdomain (recommended) | https://gaurangga.mahalaksmi.web.id |
| Direct Landing | https://prahlad168.github.io/Alpha-agent-Gaurangga/mahalaksmi-web.html |
| Main App | https://prahlad168.github.io/Alpha-agent-Gaurangga/app/main.html |

---

## 🆘 Troubleshooting

### Error: CNAME File Already Exists
Hapus CNAME lama dan buat yang baru.

### Error: HTTPS Not Working
Tunggu 5-10 menit setelah save, lalu clear browser cache.

### Error: 404 After Setup
Pastikan DNS sudah propagate: https://dnschecker.org/

### Error: Too Many Redirects
Pastikan tidak ada redirect loop di Cloudflare/registrar.

---

**Version:** 1.0.0 | **Created:** 2026-07-18 | **Status:** 🚀 READY TO SETUP
