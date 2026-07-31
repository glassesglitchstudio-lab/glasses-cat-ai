/* GlassesCat Global Skill Library - executable skills (fonksiyon tabanlı) */
window.SKILL_LIBRARY = [
{
    id:'hesapla', name:'Hesaplama', icon:'🧮',
    desc:'Matematiksel ifadeleri ve yüzdeleri çözer',
    example:'150 ile 30 topla',
    keywords:['hesapla','kaç eder','topla','çıkar','çarp','böl','yüzde'],
    match:/\d\s*[\+\-\*xX%\/]\s*\d/,
    run:function(t){
        var txt=t.toLowerCase().replace(/,/g,'.');
        var op=null;
        if(/topla|artı/.test(txt)||txt.indexOf('+')>=0) op='+';
        else if(/çıkar|eksi/.test(txt)||txt.indexOf('-')>=0) op='-';
        else if(/çarp|çarpı/.test(txt)||txt.indexOf('*')>=0||/[xX]/.test(txt)) op='*';
        else if(/böl|bölü/.test(txt)||txt.indexOf('/')>=0) op='/';
        else if(/yüzde|%/.test(txt)) op='%';
        if(!op) return {ok:false};
        var nums=(txt.match(/\d+(?:\.\d+)?/g)||[]).map(parseFloat).slice(0,2);
        if(nums.length<2) return {ok:false};
        var a=nums[0],b=nums[1],val;
        if(op==='+') val=a+b;
        else if(op==='-') val=a-b;
        else if(op==='*') val=a*b;
        else if(op==='/') val=b===0?NaN:a/b;
        else val=a*b/100;
        if(isNaN(val)) return {ok:false};
        var opTxt=op==='+'?'+':op==='-'?'-':op==='*'?'x':op==='/'?'/':'%';
        return {ok:true,text:a+' '+opTxt+' '+b+' = **'+(Math.round(val*1e6)/1e6)+'**'};
    }
},
{
    id:'birim-cevir', name:'Birim Çevirme', icon:'📏',
    desc:'km/mil, kg/lb, m/ft, litre/galon, C/F dönüşümü',
    example:'5 km kaç mil',
    keywords:['çevir','kaç mil','kaç km','kaç pound','kaç libre','kaç feet','kaç galon','fahrenheit','celsius'],
    run:function(t){
        var txt=t.toLowerCase();
        var m=txt.match(/(\d+(?:\.\d+)?)\s*(km|mil|kg|pound|libre|m|ft|feet|l|lt|litre|galon|c|f)/);
        if(!m) return {ok:false};
        var v=parseFloat(m[1]),u=m[2],out=null,outU='';
        if(u==='km'){out=v/1.609;outU='mil';}
        else if(u==='mil'){out=v*1.609;outU='km';}
        else if(u==='kg'){out=v*2.205;outU='lb';}
        else if(u==='pound'||u==='libre'){out=v/2.205;outU='kg';}
        else if(u==='m'){out=v*3.281;outU='ft';}
        else if(u==='ft'||u==='feet'){out=v/3.281;outU='m';}
        else if(u==='l'||u==='lt'||u==='litre'){out=v/3.785;outU='galon';}
        else if(u==='galon'){out=v*3.785;outU='litre';}
        else if(u==='c'){out=v*9/5+32;outU='F';}
        else if(u==='f'){out=(v-32)*5/9;outU='C';}
        if(out===null) return {ok:false};
        return {ok:true,text:v+' '+u+' = **'+(Math.round(out*1000)/1000)+' '+outU+'**'};
    }
},
{
    id:'sifre-uretici', name:'Şifre Üretici', icon:'🔑',
    desc:'Güçlü rastgele şifre üretir',
    example:'şifre üret 16',
    keywords:['şifre üret','şifre oluştur','password üret'],
    run:function(t){
        var m=t.match(/\d+/);
        var n=Math.min(32,Math.max(8,m?parseInt(m[0]):12));
        var chars='ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789!@#$%&*';
        var p='';
        for(var i=0;i<n;i++) p+=chars.charAt(Math.floor(Math.random()*chars.length));
        return {ok:true,text:'**'+p+'**\n\n`'+n+'` karakterli güçlü şifre üretildi.'};
    }
},
{
    id:'kelime-sayaci', name:'Kelime Sayacı', icon:'🔢',
    desc:'Metnin kelime, harf ve cümle sayısını hesaplar',
    example:'kelime say: merhaba dünya',
    keywords:['kelime say','harf say','kelime sayacı'],
    run:function(t){
        var txt=t.replace(/^[^:(]*[:(]\s*/,'').trim();
        if(txt.length<3) return {ok:false};
        var words=txt.split(/\s+/).filter(Boolean);
        var letters=txt.replace(/\s+/g,'').length;
        var sentences=(txt.match(/[.!?…]+/g)||[]).length||1;
        return {ok:true,text:'Metin: "'+txt.slice(0,60)+(txt.length>60?'…':'')+'"\n\n- Kelime: **'+words.length+'**\n- Harf: **'+letters+'**\n- Cümle: **'+sentences+'**'};
    }
},
{
    id:'json-duzenleyici', name:'JSON Düzenleyici', icon:'📦',
    desc:'Tek satır veya bozuk JSON u sıralar ve doğrular',
    example:'json düzenle: {"a":1,"b":[2,3]}',
    keywords:['json düzenle','json biçimle','json formatla'],
    run:function(t){
        var i=t.indexOf('{');
        if(i<0) return {ok:false};
        try{
            var obj=JSON.parse(t.slice(i));
            return {ok:true,text:'```json\n'+JSON.stringify(obj,null,2)+'\n```'};
        }catch(e){
            return {ok:true,text:'JSON geçersiz: '+e.message};
        }
    }
},
{
    id:'yas-hesapla', name:'Yaş Hesaplama', icon:'🎂',
    desc:'Doğum yılından yaş hesaplar',
    example:'1990 doğumluyum kaç yaşındayım',
    keywords:['doğum','doğdum','yaşım','kaç yaşında','yaş hesapla'],
    run:function(t){
        var m=t.match(/(19|20)\d{2}/);
        if(!m) return {ok:false};
        var y=parseInt(m[0]);
        if(y<1900||y>2100) return {ok:false};
        var now=new Date().getFullYear();
        var age=now-y;
        return {ok:true,text:'**'+y+'** doğumlu — bugün **'+now+'** itibarıyla **'+age+' yaşında**.'};
    }
},
{
    id:'tarih-farki', name:'Tarih Farkı', icon:'📅',
    desc:'İki tarih arasındaki gün sayısını hesaplar',
    example:'01.01.2026 ile 01.06.2026 arası kaç gün',
    keywords:['kaç gün','gün kaldı','tarih farkı','arası kaç gün'],
    run:function(t){
        function parse(d){
            var p=d.split(/[./-]/);
            var day=+p[0],mon=+p[1],yr=+p[2];
            if(yr<100) yr+=2000;
            return new Date(yr,mon-1,day);
        }
        var ds=(t.match(/\d{1,2}[./-]\d{1,2}[./-]\d{2,4}/g)||[]);
        if(ds.length===0) return {ok:false};
        var a=parse(ds[0]),b=ds.length>1?parse(ds[1]):new Date();
        var days=Math.abs(Math.round((b-a)/(86400000)));
        if(ds.length===1) return {ok:true,text:'**'+ds[0]+'** tarihine **'+days+' gün** kaldı.'};
        return {ok:true,text:ds[0]+' ile '+ds[1]+' arasında **'+days+' gün** var.'};
    }
},
{
    id:'asal-kontrol', name:'Asal Sayı', icon:'🔢',
    desc:'Sayının asal olup olmadığını kontrol eder',
    example:'17 asal mı',
    keywords:['asal mı','asal kontrol'],
    run:function(t){
        var m=t.match(/\d+/);
        if(!m) return {ok:false};
        var n=parseInt(m[0]);
        if(n<2) return {ok:true,text:n+' asal değil.'};
        var prime=true;
        for(var i=2;i*i<=n;i++) if(n%i===0){prime=false;break;}
        return {ok:true,text:'**'+n+'** '+(prime?'asal bir sayıdır ✅':'asal değildir ❌')};
    }
},
{
    id:'fibonacci', name:'Fibonacci', icon:'🌀',
    desc:'Fibonacci dizisini üretir',
    example:'fibonacci 12',
    keywords:['fibonacci'],
    run:function(t){
        var m=t.match(/\d+/);
        var n=Math.min(40,m?parseInt(m[0]):10);
        var seq=[0,1];
        for(var i=2;i<n;i++) seq.push(seq[i-1]+seq[i-2]);
        return {ok:true,text:'İlk **'+n+'** Fibonacci terimi:\n\n'+seq.join(', ')};
    }
},
{
    id:'faktoriyel', name:'Faktoriyel', icon:'❗',
    desc:'n! hesaplar',
    example:'faktoriyel 6',
    keywords:['faktoriyel','faktöriyel'],
    run:function(t){
        var m=t.match(/\d+/);
        if(!m) return {ok:false};
        var n=parseInt(m[0]);
        if(n>170) return {ok:false};
        var r=1;
        for(var i=2;i<=n;i++) r*=i;
        return {ok:true,text:n+'! = **'+r.toLocaleString('tr-TR')+'**'};
    }
},
{
    id:'rastgele-sayi', name:'Rastgele Sayı', icon:'🎲',
    desc:'Belirtilen aralıkta rastgele sayı üretir',
    example:'1 ile 100 arası rastgele',
    keywords:['rastgele','random sayı','zar at'],
    run:function(t){
        var nums=(t.match(/\d+/g)||[]).map(parseFloat);
        var lo=nums.length?Math.min(nums[0],nums[nums.length-1]):1;
        var hi=nums.length>1?Math.max(nums[0],nums[nums.length-1]):100;
        var v=Math.floor(Math.random()*(hi-lo+1))+lo;
        return {ok:true,text:'🎲 **'+lo+' - '+hi+'** aralığında: **'+v+'**'};
    }
},
{
    id:'ters-metin', name:'Ters Çevirici', icon:'🔃',
    desc:'Metni tersine çevirir',
    example:'ters çevir: merhaba',
    keywords:['ters çevir','tersine çevir','reverse'],
    run:function(t){
        var txt=t.replace(/^[^:(]*[:(]\s*/,'').trim();
        if(txt.length<2) return {ok:false};
        return {ok:true,text:'"'+txt.split('').reverse().join('')+'"'};
    }
},
{
    id:'buyuk-harf', name:'Büyük/Küçük Harf', icon:'🔠',
    desc:'Metni büyük veya küçük harfe çevirir',
    example:'büyük harf yap: merhaba',
    keywords:['büyük harf','küçük harf','uppercase','lowercase'],
    run:function(t){
        var txt=t.replace(/^[^:(]*[:(]\s*/,'').trim();
        if(txt.length<2) return {ok:false};
        if(/küçük|kucuk|lower/.test(t)) return {ok:true,text:txt.toLowerCase()};
        return {ok:true,text:txt.toUpperCase()};
    }
},
{
    id:'kisaltma', name:'Metin Kısaltma', icon:'✂️',
    desc:'Uzun metni istenen karakter sayısına kısaltır',
    example:'kısalt 50: çok uzun bir metin...',
    keywords:['kısalt','özetle','shorten'],
    run:function(t){
        var txt=t.replace(/^[^:(]*[:(]\s*/,'').trim();
        var m=t.match(/\d+/);
        var n=Math.min(500,m?parseInt(m[0]):100);
        if(txt.length<2) return {ok:false};
        if(txt.length<=n) return {ok:true,text:txt};
        return {ok:true,text:txt.slice(0,n)+'…\n\n_(**'+txt.length+'** karakter → **'+n+'** karakter)_'};
    }
},
{
    id:'kdv-hesapla', name:'KDV Hesaplama', icon:'🧾',
    desc:'KDV tutarı ve genel toplamı hesaplar',
    example:'200 tl %20 kdv',
    keywords:['kdv','vergi'],
    run:function(t){
        var nums=(t.match(/\d+(?:[.,]\d+)?/g)||[]).map(function(x){return parseFloat(x.replace(',','.'))});
        if(nums.length<2) return {ok:false};
        var amt=nums[0],pct=nums[1];
        var tax=Math.round(amt*pct/100*100)/100;
        return {ok:true,text:amt+' TL, %'+pct+' KDV:\n\n- KDV tutarı: **'+tax+' TL**\n- Genel toplam: **'+(amt+tax)+' TL**'};
    }
},
{
    id:'quiz', name:'Mini Quiz', icon:'❓',
    desc:'Rastgele bilgi sorusu sorar ve cevabını verir',
    example:'quiz yap',
    keywords:['quiz','soru sor','bilgi yarışması'],
    run:function(){
        var qs=[
            {q:'Hangi gezegen Güneş e en yakındır?',a:'Merkür'},
            {q:'Python un yaratıcısı kimdir?',a:'Guido van Rossum'},
            {q:'HTML açılımı nedir?',a:'HyperText Markup Language'},
            {q:'Bir baytta kaç bit vardır?',a:'8'},
            {q:'HTTP hangi portu kullanır?',a:'80'},
            {q:'Türkiye nin başkenti neresidir?',a:'Ankara'}
        ];
        var q=qs[Math.floor(Math.random()*qs.length)];
        return {ok:true,text:'**Soru:** '+q.q+'\n\n**Cevap:** '+q.a};
    }
}
];
