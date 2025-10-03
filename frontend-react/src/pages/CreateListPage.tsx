import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle2, Loader2 } from 'lucide-react';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { useCreatePackingList } from '@/hooks/usePackingListMutations';
import { createPackingListSchema } from '@/lib/schemas';
import type { CreatePackingListInput } from '@/lib/schemas';

const PACKING_LIST_TYPES = [
  { value: 'course', label: 'Course' },
  { value: 'selection', label: 'Selection' },
  { value: 'training', label: 'Training' },
  { value: 'deployment', label: 'Deployment' },
  { value: 'other', label: 'Other' },
];

export function CreateListPage() {
  const navigate = useNavigate();
  const createMutation = useCreatePackingList();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isValid },
  } = useForm<CreatePackingListInput>({
    resolver: zodResolver(createPackingListSchema),
    defaultValues: {
      type: 'course',
    },
    mode: 'onChange', // Enable real-time validation
  });

  const selectedType = watch('type');

  const onSubmit = async (data: CreatePackingListInput) => {
    setIsSubmitting(true);
    try {
      const result = await createMutation.mutateAsync(data);
      setIsSuccess(true);
      toast.success('Packing list created successfully!');

      // Delay navigation to show success animation
      setTimeout(() => {
        navigate(`/list/${result.data.id}`);
      }, 800);
    } catch (error) {
      toast.error('Failed to create packing list. Please try again.');
      console.error('Failed to create packing list:', error);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <Button
          variant="secondary"
          onClick={() => navigate('/')}
          className="mb-4"
          disabled={isSubmitting}
        >
          <ArrowLeft className="inline mr-2" size={16} />
          Back to Lists
        </Button>
        <h1 className="text-3xl font-bold text-military-dark">Create New Packing List</h1>
        <p className="text-gray-600 mt-2">Build your mission-ready checklist in minutes</p>
      </div>

      <Card className={`transition-all duration-300 ${isSuccess ? 'border-status-complete bg-status-complete/5' : ''}`}>
        {isSuccess ? (
          <div className="py-8 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-status-complete/10 rounded-full mb-4">
              <CheckCircle2 className="text-status-complete" size={32} />
            </div>
            <h2 className="text-2xl font-bold text-military-dark mb-2">List Created!</h2>
            <p className="text-gray-600">Redirecting to your new packing list...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)}>
            <Input
              label="List Name *"
              placeholder="e.g., Ranger School Packing List"
              error={errors.name?.message}
              disabled={isSubmitting}
              {...register('name')}
            />

            <div className="mb-4">
              <label className="block text-sm font-medium text-military-dark mb-1">
                Description
              </label>
              <textarea
                placeholder="Describe what this packing list is for..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-military-navy focus:border-transparent transition-colors duration-200 disabled:bg-gray-50 disabled:cursor-not-allowed"
                rows={4}
                disabled={isSubmitting}
                {...register('description')}
              />
              {errors.description && (
                <p className="mt-1 text-sm text-status-required">{errors.description.message}</p>
              )}
            </div>

            <Select
              label="List Type *"
              options={PACKING_LIST_TYPES}
              error={errors.type?.message}
              disabled={isSubmitting}
              {...register('type')}
            />

            {selectedType === 'other' && (
              <Input
                label="Custom Type"
                placeholder="Specify custom type"
                error={errors.custom_type?.message}
                disabled={isSubmitting}
                {...register('custom_type')}
              />
            )}

            <div className="flex gap-4 mt-6">
              <Button
                type="submit"
                variant="success"
                disabled={isSubmitting}
                className="relative"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="inline mr-2 animate-spin" size={16} />
                    Creating List...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="inline mr-2" size={16} />
                    Create List
                  </>
                )}
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={() => navigate('/')}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
            </div>
          </form>
        )}
      </Card>

      {/* Helper Tips */}
      {!isSuccess && (
        <Card className="mt-6 bg-military-sand/10 border-military-sand/30">
          <h3 className="font-semibold text-military-dark mb-2 flex items-center gap-2">
            <span className="text-xl">💡</span>
            Pro Tips
          </h3>
          <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
            <li>Use a descriptive name that clearly identifies the purpose</li>
            <li>Select the correct type to help categorize your list</li>
            <li>Add a detailed description to help others understand the context</li>
          </ul>
        </Card>
      )}
    </div>
  );
}
