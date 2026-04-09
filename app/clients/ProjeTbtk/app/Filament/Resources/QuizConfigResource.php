<?php

namespace App\Filament\Resources;

use App\Filament\Resources\QuizConfigResource\Pages;
use App\Models\QuizConfig;
use App\Models\Unit;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;

class QuizConfigResource extends Resource
{
    protected static ?string $model = QuizConfig::class;

    protected static ?string $navigationIcon = 'heroicon-o-rectangle-stack';
    protected static ?string $navigationLabel = 'Quiz Ayarlari';
    protected static ?string $modelLabel = 'Quiz Ayari';
    protected static ?string $pluralModelLabel = 'Quiz Ayarlari';
    protected static ?string $navigationGroup = 'Icerik';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Select::make('unit_id')
                    ->label('Unite')
                    ->options(
                        Unit::query()
                            ->orderBy('grade')
                            ->orderBy('unit_no')
                            ->get()
                            ->mapWithKeys(fn (Unit $unit) => [
                                $unit->id => $unit->grade . '. Sinif / ' . $unit->unit_no . '. Unite - ' . $unit->name,
                            ])
                            ->all()
                    )
                    ->searchable()
                    ->required(),
                Forms\Components\Select::make('quiz_type')
                    ->label('Quiz Tipi')
                    ->options([
                        'flashcard' => 'Flashcard',
                        'mcq' => 'MCQ',
                        'matching' => 'Matching',
                        'fill_blank' => 'Fill Blank',
                    ])
                    ->required(),
                Forms\Components\TextInput::make('question_count')
                    ->label('Soru Sayisi')
                    ->required()
                    ->numeric()
                    ->minValue(1)
                    ->maxValue(50),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('unit.name')
                    ->label('Unite')
                    ->searchable(),
                Tables\Columns\TextColumn::make('quiz_type')
                    ->label('Quiz Tipi')
                    ->badge(),
                Tables\Columns\TextColumn::make('question_count')
                    ->label('Soru Adedi')
                    ->sortable(),
            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\ViewAction::make(),
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListQuizConfigs::route('/'),
            'create' => Pages\CreateQuizConfig::route('/create'),
            'view' => Pages\ViewQuizConfig::route('/{record}'),
            'edit' => Pages\EditQuizConfig::route('/{record}/edit'),
        ];
    }

    public static function getEloquentQuery(): Builder
    {
        return parent::getEloquentQuery()->with('unit');
    }
}
