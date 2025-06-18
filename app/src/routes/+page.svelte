<script>
  import { onMount } from 'svelte';
  import PlanCard from '$lib/PlanCard.svelte';

  let area = '';
  let checkin = '';
  let checkout = '';
  let rooms = 1;
  let guests = 1;
  let min_price = '';
  let max_price = '';
  let dinner = false;

  let hotelPhotos = [];
  let roomPhotos = [];
  let rawResults = [];
  let groupedResults = [];
  let expandedHotels = new Set();

  let loading = false;
  let error = '';

  function today(offset = 0) {
    const d = new Date();
    d.setDate(d.getDate() + offset);
    return d.toISOString().slice(0, 10);
  }

  onMount(async () => {
    checkin = today(1);
    checkout = today(7);

    try {
      const res = await fetch('http://localhost:8888/api/photos');
      if (!res.ok) throw new Error('写真APIエラー');
      const data = await res.json();
      hotelPhotos = data.hotel_photos;
      roomPhotos = data.room_photos;
    } catch (e) {
      error = '写真リストの取得に失敗しました';
    }
  });

  async function search() {
    loading = true;
    error = '';
    rawResults = [];
    groupedResults = [];
    expandedHotels = new Set();

    const params = new URLSearchParams();
    if (area) params.append('area', area);
    if (checkin) params.append('checkin', checkin);
    if (checkout) params.append('checkout', checkout);
    if (rooms) params.append('rooms', rooms);
    if (guests) params.append('guests', guests);
    if (min_price) params.append('min_price', min_price);
    if (max_price) params.append('max_price', max_price);
    if (dinner) params.append('dinner', 'true');

    try {
      const res = await fetch(`http://localhost:8888/api/search?${params.toString()}`);
      if (!res.ok) throw new Error('検索APIエラー');
      const results = await res.json();
      rawResults = results.map(r => ({
        ...r,
        hotel_photo: hotelPhotos.length ? hotelPhotos[Math.floor(Math.random() * hotelPhotos.length)] : '',
        room_photo: roomPhotos.length ? roomPhotos[Math.floor(Math.random() * roomPhotos.length)] : ''
      }));
      groupByHotel();
    } catch (e) {
      error = e.message;
    }
    loading = false;
  }

  function groupByHotel() {
    const map = new Map();
    for (const entry of rawResults) {
      if (!map.has(entry.hotel_id)) {
        map.set(entry.hotel_id, {
          hotel_name: entry.hotel_name,
          area: entry.area,
          hotel_photo: entry.hotel_photo,
          plans: []
        });
      }
      map.get(entry.hotel_id).plans.push(entry);
    }
    groupedResults = Array.from(map.values());
  }

  function toggleExpand(hotel_name) {
    if (expandedHotels.has(hotel_name)) {
      expandedHotels.delete(hotel_name);
    } else {
      expandedHotels.add(hotel_name);
    }
    expandedHotels = new Set(expandedHotels);
  }
</script>

<style>
  .search-form {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 2rem;
    background: #f9f9f9;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 8px #0001;
  }
  .search-form label {
    display: flex;
    flex-direction: column;
    font-size: 0.95em;
    min-width: 160px;
  }
  .search-form input[type="checkbox"] {
    width: 1.2em;
    height: 1.2em;
    margin-right: 0.5em;
  }
  .results-title {
    margin-top: 2rem;
    margin-bottom: 1rem;
    font-size: 1.2em;
    font-weight: bold;
    color: #1e88e5;
  }
  .hotel-list {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }
  .hotel-card {
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 8px #0002;
    overflow: hidden;
    display: flex;
    flex-direction: row;
    margin-bottom: 1.5rem;
    transition: box-shadow 0.2s;
    min-height: 180px;
  }
  .hotel-card:hover {
    box-shadow: 0 4px 16px #0004;
  }
  .hotel-photo {
    width: 180px;
    height: 180px;
    object-fit: cover;
    background: #eee;
    flex-shrink: 0;
  }
  .hotel-info {
    flex: 1;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  .plan-list {
    margin-top: 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.7rem;
  }
  .expand-btn {
    margin-top: 0.7em;
    padding: 0.3em 1.2em;
    background: #e3f2fd;
    border: none;
    border-radius: 6px;
    color: #1565c0;
    cursor: pointer;
    font-size: 1em;
    transition: background 0.2s;
  }
  .expand-btn:hover {
    background: #bbdefb;
  }
</style>

<h2>ホテル横断検索デモ</h2>
<form class="search-form" on:submit|preventDefault={search}>
  <label>
    エリア（部分一致可）
    <input type="text" bind:value={area} placeholder="例: York, Paris, Tokyo" />
  </label>
  <label>
    チェックイン
    <input type="date" bind:value={checkin} />
  </label>
  <label>
    チェックアウト
    <input type="date" bind:value={checkout} />
  </label>
  <label>
    部屋数
    <input type="number" min="1" bind:value={rooms} />
  </label>
  <label>
    人数
    <input type="number" min="1" bind:value={guests} />
  </label>
  <label>
    最低価格
    <input type="number" min="0" bind:value={min_price} placeholder="例: 10000" />
  </label>
  <label>
    最高価格
    <input type="number" min="0" bind:value={max_price} placeholder="例: 30000" />
  </label>
  <label style="align-items: center;">
    <input type="checkbox" bind:checked={dinner} />
    夕食付きのみ
  </label>
  <button type="submit" class="expand-btn" style="background:#1e88e5;color:#fff;">検索</button>
</form>

{#if loading}
  <p>検索中...</p>
{:else if error}
  <p style="color:red;">{error}</p>
{:else if groupedResults.length === 0}
  <p>検索結果はありません。</p>
{:else}
  <div class="results-title">検索結果：{groupedResults.length}ホテル</div>
  <div class="hotel-list">
    {#each groupedResults as hotel}
      <div class="hotel-card">
        <img class="hotel-photo" src={hotel.hotel_photo} alt="ホテル写真" />
        <div class="hotel-info">
          <div style="font-weight:bold;font-size:1.1em;">{hotel.hotel_name}</div>
          <div>{hotel.area}</div>
          <div class="plan-list">
            {#if !expandedHotels.has(hotel.hotel_name)}
              <PlanCard plan={hotel.plans[0]} />
            {:else}
              {#each hotel.plans as plan}
                <PlanCard {plan} />
              {/each}
            {/if}
          </div>
          {#if hotel.plans.length > 1}
            <button class="expand-btn" on:click={() => toggleExpand(hotel.hotel_name)}>
              {expandedHotels.has(hotel.hotel_name) ? '閉じる' : `もっと見る（${hotel.plans.length-1}件）`}
            </button>
          {/if}
        </div>
      </div>
    {/each}
  </div>
{/if}
