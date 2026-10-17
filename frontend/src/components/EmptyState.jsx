export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="empty-state">
      {Icon && <Icon size={48} className="empty-state-icon" />}
      <div className="empty-state-title">{title}</div>
      <p className="empty-state-desc">{description}</p>
      {action && (
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          {action}
        </div>
      )}
    </div>
  );
}
