# Bangladesh-first AI Suite — V5 (32 stand-alone Work Master Prompts)

আগের ৪টি নির্মিত সাইট: **BanglaRead Coach, DokanLens AI, BazarCompare AI, ChuktiShield AI** — আগের V3 Upgrade Prompt verbatim intact. এগুলোতে নতুন repo বানানোর বদলে existing repo-তে code/data না মুছে আপগ্রেড।
বাকি ২৮টি: V4 prompt verbatim intact, তার আগে নতুন V5 real-model requirement। ৩২টির সবগুলোর জন্য একেকটি `MASTER_PROMPT_V5.md` আছে, কোনো আলাদা common prompt ছাড়াই Work-এ ব্যবহারযোগ্য।

**নতুন V5 বাধ্যতামূলক:** সত্যিকারের inference model model_id ও smoke test সহ; AI unavailable হলে ভুয়া ফলাফল নয়। ShikkhaRAG BD-তে শুধু RAG interface নয়, embedding checkpoint, real vector/hybrid retrieval, edition/source permissions, citations, refusal, verified tests; লিঙ্ক ও example implementation আছে।

**বাংলাদেশ ডেটা:** সরকারী সোর্সের live URL, যাচাইকৃত লাইসেন্সের শর্ত, public web/reference-only আলাদা, opt-in/anonymized Bangladesh-generated data alternate, manual admin import. কোনো নতুন official dataset row ডাউনলোড বা train করে এই ফাইলে আছে—এমন দাবি নেই।

**GitHub:** ৩২টি স্বাধীন code repository-র জন্য CSV plan আছে; repo এখনো তৈরি বা push করা হয়নি। GitHub write approval, code build and model evaluation সম্পন্ন হলে Work-এ push হবে; আগের ৪টির existing repo reuse।

### How to use
1. ZIP extract করে `projects/NN_slug/MASTER_PROMPT_V5.md` নিয়ে নতুন Work task-এ দাও। সম্ভব হলে পুরো ওই project folder attach করো।
2. Existing site হলে Work-এ connected source GitHub repository দাও বা browse করতে অনুমতি দাও। পুরোনো DB export/backups ও app versions আগে check।
3. Model test ও admin/data workflow বাস্তবে চালাতে বলো এবং run output/commit SHA verify করো।
4. `GITHUB_32_REPOSITORIES.csv` দিয়ে ৩২টি আলাদা repositories track করো।

### Important limitations
Models checkpoints not inside ZIP; downloading & running them can require considerable RAM/CPU/GPU/hosting. The included original starter taxonomies and test cases are not verified live government measurements or permission-cleared clinical training data. BanglaBERT and Meta MMS non-commercial licenses and Ultralytics AGPL obligations must be reviewed for commercial apps; V5 prioritizes more permissive candidates.
