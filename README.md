
## Crack the browser-based UUIDv4 generation
    
```js
const random_uuid = uuidv4();
    function uuidv4() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
        .replace(/[xy]/g, function (c) {
            const r = Math.random() * 16 | 0,
                v = c == 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
        });
    }
```
## Credit: Astrid (Kalmaruniomen) https://github.com/kalmarunionenctf/kalmarctf/tree/main/2025/web/spukhafte/solution
