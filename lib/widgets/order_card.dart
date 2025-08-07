import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../core/theme/app_theme.dart';
import '../models/order.dart';

class OrderCard extends StatelessWidget {
  final Order order;
  final VoidCallback? onTap;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  const OrderCard({
    super.key,
    required this.order,
    this.onTap,
    this.onEdit,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          order.orderId,
                          style: const TextStyle(
                            color: AppTheme.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          order.itemName,
                          style: TextStyle(
                            color: AppTheme.grey,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                  _buildStatusChip(),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  _buildInfoItem(
                    Icons.shopping_cart,
                    'Qty: ${order.quantity}',
                  ),
                  const SizedBox(width: 16),
                  _buildInfoItem(
                    Icons.attach_money,
                    '\$${order.totalAmount.toStringAsFixed(2)}',
                  ),
                  const SizedBox(width: 16),
                  _buildInfoItem(
                    Icons.schedule,
                    _formatTime(order.createdAt),
                  ),
                ],
              ),
              if (onEdit != null || onDelete != null) ...[
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    if (onEdit != null)
                      TextButton.icon(
                        onPressed: onEdit,
                        icon: const Icon(Icons.edit, size: 16),
                        label: const Text('Edit'),
                        style: TextButton.styleFrom(
                          foregroundColor: AppTheme.primaryYellow,
                        ),
                      ),
                    if (onDelete != null) ...[
                      const SizedBox(width: 8),
                      TextButton.icon(
                        onPressed: onDelete,
                        icon: const Icon(Icons.delete, size: 16),
                        label: const Text('Delete'),
                        style: TextButton.styleFrom(
                          foregroundColor: AppTheme.errorRed,
                        ),
                      ),
                    ],
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusChip() {
    Color statusColor;
    switch (order.status.toLowerCase()) {
      case 'pending':
        statusColor = AppTheme.warningOrange;
        break;
      case 'processing':
        statusColor = AppTheme.infoBlue;
        break;
      case 'completed':
        statusColor = AppTheme.successGreen;
        break;
      case 'cancelled':
      case 'failed':
        statusColor = AppTheme.errorRed;
        break;
      default:
        statusColor = AppTheme.grey;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: statusColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: statusColor.withOpacity(0.3)),
      ),
      child: Text(
        order.statusDisplay,
        style: TextStyle(
          color: statusColor,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildInfoItem(IconData icon, String text) {
    return Row(
      children: [
        Icon(
          icon,
          size: 16,
          color: AppTheme.grey,
        ),
        const SizedBox(width: 4),
        Text(
          text,
          style: TextStyle(
            color: AppTheme.grey,
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final difference = now.difference(time);

    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m ago';
    } else {
      return 'Just now';
    }
  }
}

class OrderListItem extends StatelessWidget {
  final Order order;
  final VoidCallback? onTap;
  final bool showActions;

  const OrderListItem({
    super.key,
    required this.order,
    this.onTap,
    this.showActions = false,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      onTap: onTap,
      leading: CircleAvatar(
        backgroundColor: _getStatusColor().withOpacity(0.1),
        child: Icon(
          Icons.shopping_cart,
          color: _getStatusColor(),
          size: 20,
        ),
      ),
      title: Text(
        order.orderId,
        style: const TextStyle(
          color: AppTheme.white,
          fontWeight: FontWeight.w600,
        ),
      ),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            order.itemName,
            style: TextStyle(
              color: AppTheme.grey,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 4),
          Row(
            children: [
              Text(
                'Qty: ${order.quantity}',
                style: TextStyle(
                  color: AppTheme.grey,
                  fontSize: 12,
                ),
              ),
              const SizedBox(width: 16),
              Text(
                '\$${order.totalAmount.toStringAsFixed(2)}',
                style: TextStyle(
                  color: AppTheme.primaryYellow,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ],
      ),
      trailing: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: _getStatusColor().withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: _getStatusColor().withOpacity(0.3)),
            ),
            child: Text(
              order.statusDisplay,
              style: TextStyle(
                color: _getStatusColor(),
                fontSize: 10,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            _formatTime(order.createdAt),
            style: TextStyle(
              color: AppTheme.grey,
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }

  Color _getStatusColor() {
    switch (order.status.toLowerCase()) {
      case 'pending':
        return AppTheme.warningOrange;
      case 'processing':
        return AppTheme.infoBlue;
      case 'completed':
        return AppTheme.successGreen;
      case 'cancelled':
      case 'failed':
        return AppTheme.errorRed;
      default:
        return AppTheme.grey;
    }
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final difference = now.difference(time);

    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m ago';
    } else {
      return 'Just now';
    }
  }
}

class OrderDetailCard extends StatelessWidget {
  final Order order;
  final VoidCallback? onStatusUpdate;

  const OrderDetailCard({
    super.key,
    required this.order,
    this.onStatusUpdate,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Order Details',
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          color: AppTheme.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        order.orderId,
                        style: TextStyle(
                          color: AppTheme.grey,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
                _buildStatusChip(),
              ],
            ),
            const SizedBox(height: 24),
            _buildDetailRow('Item', order.itemName),
            _buildDetailRow('Slot', 'Slot ${order.slotId}'),
            _buildDetailRow('Quantity', order.quantity.toString()),
            _buildDetailRow('Price', '\$${order.price.toStringAsFixed(2)}'),
            _buildDetailRow('Total', '\$${order.totalAmount.toStringAsFixed(2)}'),
            _buildDetailRow('Status', order.statusDisplay),
            _buildDetailRow('Type', order.orderType),
            _buildDetailRow('Created', _formatDateTime(order.createdAt)),
            _buildDetailRow('Updated', _formatDateTime(order.updatedAt)),
            if (order.completedAt != null)
              _buildDetailRow('Completed', _formatDateTime(order.completedAt!)),
            if (order.userName != null)
              _buildDetailRow('Customer', order.userName!),
            if (order.ipAddress != null)
              _buildDetailRow('IP Address', order.ipAddress!),
            if (order.errorMessage != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.errorRed.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppTheme.errorRed.withOpacity(0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.error_outline,
                          color: AppTheme.errorRed,
                          size: 16,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Error Message',
                          style: TextStyle(
                            color: AppTheme.errorRed,
                            fontWeight: FontWeight.w600,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      order.errorMessage!,
                      style: TextStyle(
                        color: AppTheme.errorRed,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              label,
              style: TextStyle(
                color: AppTheme.grey,
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                color: AppTheme.white,
                fontSize: 14,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusChip() {
    Color statusColor;
    switch (order.status.toLowerCase()) {
      case 'pending':
        statusColor = AppTheme.warningOrange;
        break;
      case 'processing':
        statusColor = AppTheme.infoBlue;
        break;
      case 'completed':
        statusColor = AppTheme.successGreen;
        break;
      case 'cancelled':
      case 'failed':
        statusColor = AppTheme.errorRed;
        break;
      default:
        statusColor = AppTheme.grey;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: statusColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: statusColor.withOpacity(0.3)),
      ),
      child: Text(
        order.statusDisplay,
        style: TextStyle(
          color: statusColor,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    return DateFormat('MMM dd, yyyy HH:mm').format(dateTime);
  }
} 