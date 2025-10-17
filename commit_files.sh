#!/bin/bash

# Commit files one by one in the posawesome directory
echo "🚀 Starting file-by-file commit process..."

# Array of files to commit
files=(
    "improvements_tasks/frontend/frontend_improvment_policy.md"
    "posawesome/posawesome/api/customer/_old_backup/__init__.py"
    "posawesome/posawesome/api/customer/_old_backup/available_credit.py"
    "posawesome/posawesome/api/customer/_old_backup/create_customer.py"
    "posawesome/posawesome/api/customer/_old_backup/customer_addresses.py"
    "posawesome/posawesome/api/customer/_old_backup/customer_groups.py"
    "posawesome/posawesome/api/customer/_old_backup/customer_info.py"
    "posawesome/posawesome/api/customer/_old_backup/customer_names.py"
    "posawesome/posawesome/api/customer/_old_backup/delete_customer.py"
    "posawesome/posawesome/api/customer/_old_backup/get_customer.py"
    "posawesome/posawesome/api/customer/_old_backup/get_customer_addresses.py"
    "posawesome/posawesome/api/customer/_old_backup/get_customer_coupons.py"
    "posawesome/posawesome/api/customer/_old_backup/get_customer_credit.py"
    "posawesome/posawesome/api/customer/_old_backup/get_many_customers.py"
    "posawesome/posawesome/api/customer/_old_backup/gift_coupon.py"
    "posawesome/posawesome/api/customer/_old_backup/hooks.py"
    "posawesome/posawesome/api/customer/_old_backup/pos_coupon.py"
    "posawesome/posawesome/api/customer/_old_backup/post_customer.py"
    "posawesome/posawesome/api/customer/_old_backup/referral_code.py"
    "posawesome/posawesome/api/customer/_old_backup/set_customer_info.py"
    "posawesome/posawesome/api/customer/_old_backup/update_customer.py"
    "posawesome/posawesome/api/customer/delete_customer.py"
    "posawesome/posawesome/api/customer/get_customer.py"
    "posawesome/posawesome/api/customer/get_customer_addresses.py"
    "posawesome/posawesome/api/customer/get_customer_balance.py"
    "posawesome/posawesome/api/customer/get_customer_coupons.py"
    "posawesome/posawesome/api/customer/get_customer_credit.py"
    "posawesome/posawesome/api/customer/get_many_customers.py"
    "posawesome/posawesome/api/customer/post_customer.py"
    "posawesome/posawesome/api/customer/update_customer.py"
    "posawesome/posawesome/api/sales_invoice/clear_locks.py"
    "posnext_customer_search_logic_analysis.md"
)

# Commit each file individually
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "📝 Committing: $file"
        
        # Add the specific file
        git add "$file"
        
        # Create a descriptive commit message based on file path
        if [[ $file == *"frontend_improvment_policy.md" ]]; then
            commit_msg="📋 Add frontend improvement policy with batch queue system"
        elif [[ $file == *"_old_backup"* ]]; then
            filename=$(basename "$file" .py)
            commit_msg="📦 Backup legacy customer API: $filename"
        elif [[ $file == *"customer/"* ]]; then
            filename=$(basename "$file" .py)
            commit_msg="✨ Implement modern customer API: $filename"
        elif [[ $file == *"sales_invoice/"* ]]; then
            filename=$(basename "$file" .py)
            commit_msg="🔧 Add sales invoice utility: $filename"
        elif [[ $file == *"posnext_customer_search_logic_analysis.md" ]]; then
            commit_msg="📊 Add POSNext customer search logic analysis"
        else
            commit_msg="📄 Update: $(basename "$file")"
        fi
        
        # Commit the file
        git commit -m "$commit_msg"
        
        if [ $? -eq 0 ]; then
            echo "✅ Successfully committed: $file"
        else
            echo "❌ Failed to commit: $file"
        fi
        
        echo "---"
        
        # Optional: Add a small delay to avoid overwhelming git
        sleep 1
    else
        echo "⚠️  File not found: $file"
    fi
done

echo "🎉 File-by-file commit process completed!"
echo "📈 Check git log to see all commits:"
echo "git log --oneline -10"