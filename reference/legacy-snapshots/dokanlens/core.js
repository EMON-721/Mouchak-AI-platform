(function(root){
function number(v){return Number(String(v).replace(/[০-৯]/g,c=>'০১২৩৪৫৬৭৮৯'.indexOf(c)).replace(/,/g,''))}
function validate(p){if(!p.name.trim())throw Error('পণ্যের নাম লিখুন');for(const key of ['stock','price','cost','low'])if(!Number.isFinite(p[key])||p[key]<0)throw Error('সঠিক শূন্য বা ধনাত্মক সংখ্যা লিখুন');if(!Number.isInteger(p.stock)||!Number.isInteger(p.low))throw Error('প্যাকেটের সংখ্যা পূর্ণসংখ্যা হতে হবে');return p}
function transact(products,id,type,quantity){const q=number(quantity);if(!Number.isInteger(q)||q<1)throw Error('কমপক্ষে ১টি পূর্ণ প্যাকেট লিখুন');const p=products.find(p=>p.id===id);if(!p)throw Error('পণ্য পাওয়া যায়নি');if(type==='sale'&&q>p.stock)throw Error('স্টকে পর্যাপ্ত পণ্য নেই');if(!['sale','purchase'].includes(type))throw Error('অজানা লেনদেন');return products.map(x=>x.id===id?{...x,stock:x.stock+(type==='sale'?-q:q)}:x)}
const api={number,validate,transact};if(typeof module!=='undefined')module.exports=api;root.Inventory=api;
})(typeof window==='undefined'?globalThis:window);
