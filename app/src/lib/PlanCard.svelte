<script>
  export let plan;
</script>

<div class="plan-card">
  <img class="room-photo" src={plan.room_photo} alt="部屋写真" />
  <div class="plan-body">
    <div class="plan-name">{plan.plan_name} / {plan.room_type}（定員: {plan.capacity}人）</div>
    <div>夕食: {plan.dinner ? 'あり' : 'なし'} / 朝食: {plan.breakfast ? 'あり' : 'なし'}</div>
    <div>空室数: {plan.min_available}</div>
    <div class="price">{plan.price.toLocaleString()}円</div>
  </div>
</div>

<style>
  .plan-card {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    background: #f7faff;
    border-radius: 6px;
    padding: 0.7rem 1rem;
    box-shadow: 0 1px 4px #0001;
  }
  .room-photo {
    width: 100px;
    height: 70px;
    object-fit: cover;
    background: #eee;
    border-radius: 4px;
    flex-shrink: 0;
  }
  .plan-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }
  .plan-name {
    font-weight: bold;
    color: #1e88e5;
    font-size: 1.05em;
  }
  .price {
    font-weight: bold;
    color: #e53935;
    font-size: 1.05em;
  }
</style>
