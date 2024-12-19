# 🎥 Midnight Cinema Bot

**Midnight Cinema Bot** — bu Telegram-kinobot bo‘lib, foydalanuvchilarga filmlar qidirish, ko‘rish va boshqarish imkonini beradi. Bot keng film bazasiga ega bo‘lib, qulay navigatsiya va aqlli qidiruv tizimi bilan jihozlangan.

## 🚀 Funksiyalar

### 🎬 Filmlar qidiruvi
- Film nomi, ID raqami, chiqarilgan yili yoki janri bo‘yicha izlash
- Xatolar va sinonimlarni hisobga oluvchi aqlli qidiruv tizimi (masalan, "Forsaj", "Forsaj 2001", "Форсаж", "forsaj")

### 📚 Film katalogi
- **Janrlar:** Filmlarni turkum bo‘yicha tezkor izlash
- **Mashhur:** Eng ko‘p tomosha qilingan filmlar
- **Yangi qo‘shilgan:** Yaqinda bazaga qo‘shilgan filmlar

### 🔧 Interaktiv boshqaruv
- **InlineKeyboardMarkup** yordamida qulay tugmalar orqali boshqarish
- Film tanlanganda eski xabar yangilanadi, yangi xabar yuborilmaydi
- Film tanlangandan so‘ng, sifatni tanlash uchun tugmalar ko‘rsatiladi va keyin film fayli guruhdan tavsifi bilan birga yuboriladi

### 📂 Avtomatik saqlash
- Har bir yuklangan film avtomatik ravishda ma'lumotlar bazasida saqlanadi
- Oldin qo‘shilgan filmlarni qayta yuklamasdan yuborish imkoniyati mavjud

## 🛠️ Texnologiyalar
- **Backend:** Python (aiogram)
- **Ma’lumotlar bazasi:** Filmlar haqidagi ma’lumotlarni saqlash va qayta ishlatish

## 📦 O‘rnatish

1. Repozitoriyani klonlang:
   ```bash
   git clone https://github.com/username/midnight-cinema-bot.git
   ```

2. Loyihaga o‘ting:
   ```bash
   cd midnight-cinema-bot
   ```

3. Virtual muhit yarating va aktivlashtiring:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate  # Windows
   ```

4. Talablarni o‘rnating:
   ```bash
   pip install -r requirements.txt
   ```

5. Botni ishga tushuring:
   ```bash
   python bot.py
   ```

## 🤝 Hissa qo‘shish
- Fork qiling
- O‘zingizning branch yarating: `git checkout -b feature/my-feature`
- O‘zgartirishlarni commit qiling: `git commit -m "Add my feature"`
- Pull request yuboring

## 📄 Litsenziya
Ushbu loyiha [MIT litsenziyasi](LICENSE) asosida tarqatiladi.

---

🎥 **Midnight Cinema Bot** sizga sevimli filmlaringizni Telegram orqali yuqori sifatda qidirish va tomosha qilish uchun qulay kino platformasini taqdim etadi! 🍿

